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
    lab = new_lecture['lab']
    days = new_lecture['days']
    start = new_lecture['starttime']
    end = new_lecture['endtime']
    
    # Convert start and end to minutes since midnight
    start_min = int(start.split(':')[0]) * 60 + int(start.split(':')[1])
    end_min = int(end.split(':')[0]) * 60 + int(end.split(':')[1])
    
    # Get existing lectures for this lab
    existing = list(collection.find({"lab": lab}))
    
    for lec in existing:
        lec_days = lec['days']
        lec_start = lec['starttime']
        lec_end = lec['endtime']
        lec_start_min = int(lec_start.split(':')[0]) * 60 + int(lec_start.split(':')[1])
        lec_end_min = int(lec_end.split(':')[0]) * 60 + int(lec_end.split(':')[1])
        
        # Check if days overlap
        for d in days:
            if d in lec_days:
                # Same day, check time overlap
                if start_min < lec_end_min and lec_start_min < end_min:
                    return True
    return False
#####################################

#starting coding the Flask app



labapp = Flask(__name__) #create the Flask app

@labapp.route('/',methods=['GET', 'POST'])
@labapp.route('/index',methods=['GET', 'POST'])
def index():
    lab = request.args.get("lab")
    if lab == None:
        lab = "1"
    
    # Fetch lectures for this lab
    lectures = list(collection.find({"lab": lab}))
    
    # Define days and times
    days = ['SUN', 'MON', 'TUE', 'WED', 'THU']
    day_map = {'1': 'SUN', '2': 'MON', '3': 'TUE', '4': 'WED', '5': 'THU'}
    times = ['08', '09', '10', '11', '12', '01', '02', '03', '04', '05', '06', '07']
    
    # Initialize schedule
    schedule = {day: {time: '' for time in times} for day in days}
    
    # Populate schedule
    for lecture in lectures:
        course = lecture.get('course', '')
        instructor = lecture.get('instructor', '')
        days_str = lecture.get('days', '')
        starttime = lecture.get('starttime', '00:00')
        endtime = lecture.get('endtime', '00:00')
        
        start_hour = int(starttime.split(':')[0])
        end_hour = int(endtime.split(':')[0])
        
        # Convert to 24-hour format if needed
        if start_hour < 8:
            start_hour += 12
        if end_hour < 8:
            end_hour += 12
        
        # Generate time slots
        time_slots = []
        for h in range(start_hour, end_hour):
            if h <= 12:
                time_slots.append(f"{h:02d}")
            else:
                time_slots.append(f"{h-12:02d}")
        
        # Assign to days
        for d in days_str:
            day_name = day_map.get(d)
            if day_name and day_name in days:
                for t in time_slots:
                    if t in times:
                        schedule[day_name][t] = f"{course} - {instructor}"
    
    return render_template('index.html', lab=lab, days=days, times=times, schedule=schedule, show_lab_tabs=True)

@labapp.route('/test',methods=['GET', 'POST'])
def test():
    labx = request.args.get("lab")
    cursor = collection.find({"lab":str(labx)}) #get lab X
    cursor.sort('starttime')  #sort by day then by start time
    user = {'username':'Samy','role':'admin'}
    title = "Lab " + str(labx) + " schedule."
    return render_template('testing.html',lab=labx,title=title,user=user,cursor=cursor)

@labapp.route('/cpanel')
def process():
    return render_template('cpanel.html', show_lab_tabs=False)

@labapp.route('/about')
def about():
    return render_template('about.html', show_lab_tabs=False)

@labapp.route('/insert_lecture', methods=['GET', 'POST']) #allow both GET and POST requests
def insert_lecture():
    course = request.args.get("course")
    days = request.args.get("days")
    starttime = request.args.get("starttime")
    endtime = request.args.get("endtime")
    numberOfStudents = request.args.get("numberOfStudents")
    lab = request.args.get("lab")
    instructor = request.args.get("instructor")
    # create lecture object
    lecture = {
    "course" : course,
    "days" : days,
    "starttime" : starttime,
    "endtime" : endtime,
    "numberOfStudents" : numberOfStudents,
    "lab" : lab,
    "instructor" : instructor
    }

    # Check for conflicts
    if has_conflict(lecture):
        return '''<html>
                  <body>
                  <h1>Conflict detected: Lab is not free during this time slot</h1>
                      <a href="/index">Home Page</a> |
                      <a href="/cpanel">Add lecture</a>
                  </body>
                  </html>'''

    # Insert Data
    lecture_id = collection.insert_one(lecture)
    #
    return '''<html>
              <body>
              <h1>Data inserted successfully</h1>
                  <a href="/index">Home Page</a> |
                  <a href="/cpanel">Add lecture</a>
              </body>
              </html>'''
#run the flask app
if __name__ == '__main__':
    labapp.run(debug=True,port=5000) #run app in debug mode on port 5000
