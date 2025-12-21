# This web app is build as a training on MONGO databases
# and FLASK framework, it's completely free , you can edit and use the code
# Creaded by Samy Abdellatif
# import required packages
import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask, request, redirect, render_template, jsonify, session, url_for
from bson.objectid import ObjectId

# Load environment variables from .env file
load_dotenv()

# basic logging
logging.basicConfig(level=logging.INFO)

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
    # Ensure a users collection exists with the default admin user.
    try:
        existing = db.list_collection_names()
        if 'users' not in existing:
            db.users.insert_one({
                'username': 'admin',
                'password': 'password',
                'role': 'admin'
            })
            logging.info('Created users collection and inserted default admin user')
        else:
            logging.info('Users collection already exists; skipping creation')
    except Exception as e:
        logging.warning('Could not ensure users collection: %s', e)
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

def has_conflict(new_lecture):
    """
    Check if the new lecture conflicts with existing lectures in the same lab.
    A conflict occurs if there's any overlap in days and time slots.
    """
    lab = new_lecture['lab']
    days = new_lecture['days']
    start = new_lecture['starttime']
    end = new_lecture['endtime']
    
    # helper to parse time strings like '08:00' into minutes since midnight
    def parse_time_min(t):
        if not t or ':' not in t:
            return None
        try:
            h = int(t.split(':')[0])
            m = int(t.split(':')[1])
            return h * 60 + m
        except Exception:
            return None

    # Convert start and end times to minutes since midnight for easy comparison
    start_min = parse_time_min(start)
    end_min = parse_time_min(end)
    if start_min is None or end_min is None:
        logging.warning('Skipping conflict check: invalid times for new_lecture: start=%r end=%r', start, end)
        return False
    
    # Retrieve all existing lectures for the specified lab
    existing = list(collection.find({"lab": lab}))
    
    for lec in existing:
        lec_days = lec['days']
        lec_start = lec['starttime']
        lec_end = lec['endtime']
        # Convert existing lecture times to minutes
        lec_start_min = parse_time_min(lec_start)
        lec_end_min = parse_time_min(lec_end)
        if lec_start_min is None or lec_end_min is None:
            logging.warning('Skipping existing lecture during conflict check due to invalid times: %r', lec)
            continue
        
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
# Secret key for session management; prefer env var
labapp.secret_key = os.getenv('FLASK_SECRET_KEY', 'change-this-secret')

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
    is_logged_in = bool(session.get('user'))
    return render_template('index.html', lab=lab, days=days, times=times, display_times=display_times, schedule=schedule, show_lab_tabs=True, is_logged_in=is_logged_in)

@labapp.route('/cpanel')
def process():
    """
    Route for the control panel page where users can add new lectures.
    """
    return render_template('cpanel.html', show_lab_tabs=False)


@labapp.route('/change_password', methods=['POST'])
def change_password():
    """Allow logged-in user to change own password stored in users collection."""
    if not session.get('user'):
        return redirect(url_for('login', next=url_for('process')))

    username = session.get('user')
    current = request.form.get('current_password')
    new = request.form.get('new_password')
    confirm = request.form.get('confirm_password')

    if not current or not new or not confirm:
        return render_template('cpanel.html', show_lab_tabs=False, error='All fields are required')
    if new != confirm:
        return render_template('cpanel.html', show_lab_tabs=False, error='New passwords do not match')
    if collection is None:
        return render_template('cpanel.html', show_lab_tabs=False, error='Database not configured')

    try:
        user_doc = db.users.find_one({'username': username})
    except Exception as e:
        logging.error('DB error fetching user: %s', e)
        return render_template('cpanel.html', show_lab_tabs=False, error='Database error')

    if not user_doc:
        return render_template('cpanel.html', show_lab_tabs=False, error='User not found')
    if user_doc.get('password') != current:
        return render_template('cpanel.html', show_lab_tabs=False, error='Current password incorrect')

    # update password (note: plaintext storage—consider hashing in future)
    try:
        db.users.update_one({'username': username}, {'$set': {'password': new}})
        return render_template('cpanel.html', show_lab_tabs=False, success='Password updated successfully')
    except Exception as e:
        logging.error('DB error updating password: %s', e)
        return render_template('cpanel.html', show_lab_tabs=False, error='Failed to update password')


@labapp.route('/get_lecture')
def get_lecture():
    """
    Return a single lecture covering the given lab/day/time, or empty JSON.
    Query params: lab (str), day (e.g. 'MON'), time (key like '08')
    """
    lab = request.args.get('lab')
    day = request.args.get('day')
    time_key = request.args.get('time')
    if not lab or not day or not time_key:
        return jsonify({})

    # map day name back to code
    rev_map = {'SUN':'1','MON':'2','TUE':'3','WED':'4','THU':'5'}
    day_code = rev_map.get(day)
    if not day_code:
        return jsonify({})

    # convert time key to minutes for comparison
    try:
        t_h = int(time_key)
    except Exception:
        return jsonify({})

    # Find candidate lectures in this lab that include the day
    candidates = list(collection.find({"lab": lab}))
    for lec in candidates:
        days = lec.get('days', '')
        if day_code in days:
            start = lec.get('starttime', '00:00')
            end = lec.get('endtime', '00:00')
            try:
                s_h = int(start.split(':')[0])
                e_h = int(end.split(':')[0])
                # normalize PM times (same heuristic as index)
                if s_h < 8:
                    s_h += 12
                if e_h < 8:
                    e_h += 12
                # normalize requested time key to comparable hour
                req_h = t_h
                if req_h < 8:
                    req_h += 12
                # check range
                if s_h <= req_h < e_h:
                    # prepare jsonable doc
                    lec_out = {k: v for k, v in lec.items() if k != '_id'}
                    lec_out['_id'] = str(lec['_id'])
                    return jsonify(lec_out)
            except Exception:
                continue
    return jsonify({})


@labapp.route('/lectures')
def lectures_for_lab():
    """Return JSON list of lectures for a given lab."""
    lab = request.args.get('lab')
    if not lab:
        return jsonify({'lectures': []})
    docs = list(collection.find({'lab': lab}))
    out = []
    for d in docs:
        o = {k: v for k, v in d.items() if k != '_id'}
        o['_id'] = str(d['_id'])
        out.append(o)
    return jsonify({'lectures': out})


@labapp.route('/update_lecture', methods=['GET', 'POST'])
def update_lecture():
    """
    Update an existing lecture by id.
    Accepts same params as insert_lecture plus 'id' of document.
    """
    if collection is None:
        return 'Database not configured', 500

    # require login
    if not session.get('user'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'unauthorized'}), 401
        return redirect(url_for('login', next=request.path))

    lec_id = request.args.get('id') or request.form.get('id')
    if not lec_id:
        return 'Missing id', 400
    try:
        oid = ObjectId(lec_id)
    except Exception:
        return 'Invalid id', 400

    # gather fields
    course = request.args.get('course') or request.form.get('course')
    days_list = request.args.getlist('days') or request.form.getlist('days')
    days = ''.join(sorted(days_list))
    starttime = request.args.get('starttime') or request.form.get('starttime')
    endtime = request.args.get('endtime') or request.form.get('endtime')
    numberOfStudents = request.args.get('numberOfStudents') or request.form.get('numberOfStudents')
    lab = request.args.get('lab') or request.form.get('lab')
    instructor = request.args.get('instructor') or request.form.get('instructor')

    # validate minimal required fields
    if not starttime or not endtime:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'starttime and endtime required'}), 400
        return 'starttime and endtime required', 400

    update = {
        'course': course,
        'days': days,
        'starttime': starttime,
        'endtime': endtime,
        'numberOfStudents': numberOfStudents,
        'lab': lab,
        'instructor': instructor,
    }

    collection.update_one({'_id': oid}, {'$set': update})
    # If AJAX call, return JSON so client can update view without reload
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        update_out = update.copy()
        update_out['_id'] = str(oid)
        return jsonify({'success': True, 'lecture': update_out})

    # After updating, redirect back to the index page for the same lab
    try:
        target_lab = lab if lab else '1'
    except Exception:
        target_lab = '1'
    return redirect(f"/index?lab={target_lab}")

@labapp.route('/about')
def about():
    """
    Route for the about page with information about the application.
    """
    return render_template('about.html', show_lab_tabs=False)


@labapp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', show_lab_tabs=False)

    # POST: authenticate
    username = request.form.get('username')
    password = request.form.get('password')
    next_url = request.args.get('next') or request.form.get('next') or url_for('index')
    user_found = db.users.find_one({"username": username})

    if user_found:
        # 2. Get the stored password (assuming it's stored as string)
        password_from_db = user_found.get('password')
        if password_from_db == password:
            session['user'] = username
            return redirect(next_url) # "Login successful!"
        else:
            return render_template('login.html', show_lab_tabs=False, error='Invalid credentials')


@labapp.route('/logout')
def logout():
    session.pop('user', None)
    # redirect back to home or referer
    ref = request.headers.get('Referer')
    if ref:
        return redirect(ref)
    return redirect(url_for('index'))

@labapp.route('/insert_lecture', methods=['GET', 'POST']) #allow both GET and POST requests
def insert_lecture():
    """
    Route to insert a new lecture into the database.
    Retrieves form data, checks for conflicts, and inserts if no conflicts exist.
    """
    if collection is None:
        return 'Database not configured', 500

    # require login to add lectures
    if not session.get('user'):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'unauthorized'}), 401
        return redirect(url_for('login', next=request.path))

    course = request.args.get("course") or request.form.get("course")
    days_list = request.args.getlist("days") or request.form.getlist("days")  # Get list of selected days from checkboxes
    days = ''.join(sorted(days_list))  # Sort and join into a string (e.g., '135')
    starttime = request.args.get("starttime") or request.form.get("starttime")
    endtime = request.args.get("endtime") or request.form.get("endtime")
    numberOfStudents = request.args.get("numberOfStudents") or request.form.get("numberOfStudents")
    lab = request.args.get("lab") or request.form.get("lab")
    instructor = request.args.get("instructor") or request.form.get("instructor")

    # validate minimal required fields
    if not starttime or not endtime:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'starttime and endtime required'}), 400
        return 'starttime and endtime required', 400
    
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
    result = collection.insert_one(lecture)

    # If request originates from AJAX, return JSON for client-side update
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        lecture_out = lecture.copy()
        lecture_out['_id'] = str(result.inserted_id)
        return jsonify({'success': True, 'lecture': lecture_out})

    # Redirect to the index page for the same lab where the lecture was inserted
    target_lab = lab if lab else '1'
    return redirect(f"/index?lab={target_lab}")
# Run the Flask application
if __name__ == '__main__':
    labapp.run(debug=True, port=5000)  # Run app in debug mode on port 5000
