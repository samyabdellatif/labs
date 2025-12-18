# This web app is build as a training on MONGO databases
# and FLASK framework, it's completely free , you can edit and use the code
# Creaded by Samy Abdellatif
# import required packages
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask, request, redirect, render_template

# Load environment variables from .env file
load_dotenv()

# Getting the data from process.html form then
# inserting data in MongoDB labsDB database
# connecting to the database
client = None
try:
    # Get MongoDB connection string from environment variable
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    client = MongoClient(mongo_uri)
    print("Connected successfully!!!")
except Exception as e:
    print(f"Could not connect to MongoDB: {e}")

# database
if client:
    db = client.labsDB
    # convert into mongoDB document object
    collection = db.lectures
else:
    print("Warning: No MongoDB connection. Database operations will fail.")
    db = None
    collection = None

# load the full database into cursor
cursor = collection.find()
# for record in cursor:
# 	print(record)

#####################################
######### GOODIES ###################
#split a string into list of characters
def split(word):
    return [char for char in word]

def has_conflict(new_lecture):
    """
    Check if the new lecture conflicts with existing lectures in the same lab.
    A conflict occurs if there's any overlap in days and time slots.
    """
    lab = new_lecture['lab']
    days = new_lecture['days']
    start = new_lecture['starttime']
    end = new_lecture['endtime']
    
    # Convert start and end times to minutes since midnight for easy comparison
    start_min = int(start.split(':')[0]) * 60 + int(start.split(':')[1])
    end_min = int(end.split(':')[0]) * 60 + int(end.split(':')[1])
    
    # Retrieve all existing lectures for the specified lab
    existing = list(collection.find({"lab": lab}))
    
    for lec in existing:
        lec_days = lec['days']
        lec_start = lec['starttime']
        lec_end = lec['endtime']
        # Convert existing lecture times to minutes
        lec_start_min = int(lec_start.split(':')[0]) * 60 + int(lec_start.split(':')[1])
        lec_end_min = int(lec_end.split(':')[0]) * 60 + int(lec_end.split(':')[1])
        
        # Check for overlapping days
        for d in days:
            if d in lec_days:
                # Check for time overlap on the same day
                if start_min < lec_end_min and lec_start_min < end_min:
                    return True  # Conflict detected
    return False  # No conflict
#####################################

#starting coding the Flask app



labapp = Flask(__name__) #create the Flask app

@labapp.route('/',methods=['GET', 'POST'])
@labapp.route('/index',methods=['GET', 'POST'])
def index():
    """
    Main index route that displays the lab schedule.
    Retrieves the lab number from query parameters, fetches lectures,
    and builds a schedule grid for display.
    """
    lab = request.args.get("lab")
    if lab == None:
        lab = "1"  # Default to lab 1 if not specified
    
    # Fetch all lectures for the selected lab from MongoDB
    lectures = list(collection.find({"lab": lab}))
    
    # Define the days of the week and their mappings
    days = ['SUN', 'MON', 'TUE', 'WED', 'THU']
    day_map = {'1': 'SUN', '2': 'MON', '3': 'TUE', '4': 'WED', '5': 'THU'}
    # Time slots in 24-hour format (internal keys)
    times = ['08', '09', '10', '11', '12', '01', '02', '03', '04', '05', '06', '07']
    # Display times in 12-hour format with AM/PM
    display_times = ['8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM']
    
    # Initialize an empty schedule grid
    schedule = {day: {time: '' for time in times} for day in days}
    
    # Populate the schedule with lecture data
    for lecture in lectures:
        course = lecture.get('course', '')
        instructor = lecture.get('instructor', '')
        days_str = lecture.get('days', '')  # String of day codes (e.g., '123' for SUN,MON,TUE)
        starttime = lecture.get('starttime', '00:00')
        endtime = lecture.get('endtime', '00:00')
        
        # Extract hour from time strings
        start_hour = int(starttime.split(':')[0])
        end_hour = int(endtime.split(':')[0])
        
        # Convert 12-hour format to 24-hour if necessary (assuming times before 8 are PM)
        if start_hour < 8:
            start_hour += 12
        if end_hour < 8:
            end_hour += 12
        
        # Generate the list of time slots covered by this lecture
        time_slots = []
        for h in range(start_hour, end_hour):
            if h <= 12:
                time_slots.append(f"{h:02d}")
            else:
                time_slots.append(f"{h-12:02d}")
        
        # Assign the lecture to the appropriate days and time slots in the schedule
        for d in days_str:
            day_name = day_map.get(d)
            if day_name and day_name in days:
                for t in time_slots:
                    if t in times:
                        schedule[day_name][t] = f"{course} - {instructor}"
    
    # Render the index template with the populated schedule
    return render_template('index.html', lab=lab, days=days, times=times, display_times=display_times, schedule=schedule, show_lab_tabs=True)

@labapp.route('/test',methods=['GET', 'POST'])
def test():
    """
    Test route to display lectures for a specific lab in a simple list format.
    Used for debugging or alternative viewing.
    """
    labx = request.args.get("lab")
    cursor = collection.find({"lab":str(labx)}) #get lab X
    cursor.sort('starttime')  #sort by day then by start time
    user = {'username':'Samy','role':'admin'}
    title = "Lab " + str(labx) + " schedule."
    return render_template('testing.html',lab=labx,title=title,user=user,cursor=cursor)

@labapp.route('/cpanel')
def process():
    """
    Route for the control panel page where users can add new lectures.
    """
    return render_template('cpanel.html', show_lab_tabs=False)

@labapp.route('/about')
def about():
    """
    Route for the about page with information about the application.
    """
    return render_template('about.html', show_lab_tabs=False)

@labapp.route('/insert_lecture', methods=['GET', 'POST']) #allow both GET and POST requests
def insert_lecture():
    """
    Route to insert a new lecture into the database.
    Retrieves form data, checks for conflicts, and inserts if no conflicts exist.
    """
    course = request.args.get("course")
    days_list = request.args.getlist("days")  # Get list of selected days from checkboxes
    days = ''.join(sorted(days_list))  # Sort and join into a string (e.g., '135')
    starttime = request.args.get("starttime")
    endtime = request.args.get("endtime")
    numberOfStudents = request.args.get("numberOfStudents")
    lab = request.args.get("lab")
    instructor = request.args.get("instructor")
    
    # Create lecture object from form data
    lecture = {
    "course" : course,
    "days" : days,
    "starttime" : starttime,
    "endtime" : endtime,
    "numberOfStudents" : numberOfStudents,
    "lab" : lab,
    "instructor" : instructor
    }

    # Check for scheduling conflicts before inserting
    if has_conflict(lecture):
        return '''<html>
                  <body>
                  <h1>Conflict detected: Lab is not free during this time slot</h1>
                      <a href="/index">Home Page</a> |
                      <a href="/cpanel">Add lecture</a>
                  </body>
                  </html>'''

    # Insert the lecture into the database
    lecture_id = collection.insert_one(lecture)
    
    # Return success message
    return '''<html>
              <body>
              <h1>Data inserted successfully</h1>
                  <a href="/index">Home Page</a> |
                  <a href="/cpanel">Add lecture</a>
              </body>
              </html>'''
# Run the Flask application
if __name__ == '__main__':
    labapp.run(debug=True, port=5000)  # Run app in debug mode on port 5000
