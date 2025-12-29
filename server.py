# Simple Flask app using MongoDB
import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
from flask import Flask, request, redirect, render_template, jsonify, session, url_for
from bson.objectid import ObjectId

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)

# Getting the data from process.html form then
# inserting data in MongoDB classroomsDB database
# connecting to the database
client = None
try:
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
    client = MongoClient(mongo_uri)
    print("Connected successfully!!!")
except Exception as e:
    print(f"Could not connect to MongoDB: {e}")

# database
if client:
    db = client.classroomsDB
    collection = db.classroom
        # Initialization remains minimal
    # ensure default user and settings
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
        # Ensure global settings document exists
        if 'settings' not in existing:
            db.settings.insert_one({'_id': 'global', 'weekdays': 'sun-thu'})
            logging.info('Initialized settings with default weekdays option sun-thu')
        else:
            # Make sure the document exists
            db.settings.update_one({'_id': 'global'}, {'$setOnInsert': {'weekdays': 'sun-thu'}}, upsert=True)
    except Exception as e:
        logging.warning('Could not ensure users collection: %s', e)
else:
    print("Warning: No MongoDB connection. Database operations will fail.")
    db = None
    collection = None

#####################################

def has_conflict(new_lecture):
    """Detect classroom time conflicts."""
    classroom = new_lecture.get('classroom')
    if not classroom:
        logging.warning('Conflict check skipped: classroom value missing')
        return False
    days = new_lecture['days']
    start = new_lecture['starttime']
    end = new_lecture['endtime']
    
    # parse HH:MM into minutes
    def parse_time_min(t):
        if not t or ':' not in t:
            return None
        try:
            h = int(t.split(':')[0])
            m = int(t.split(':')[1])
            return h * 60 + m
        except Exception:
            return None

    # normalize times
    start_min = parse_time_min(start)
    end_min = parse_time_min(end)
    if start_min is None or end_min is None:
        logging.warning('Skipping conflict check: invalid times for new_lecture: start=%r end=%r', start, end)
        return False
    
    # lectures for this classroom
    existing = list(collection.find({"classroom": classroom}))
    
    for lec in existing:
        lec_days = lec['days']
        lec_start = lec['starttime']
        lec_end = lec['endtime']
        # convert lecture times
        lec_start_min = parse_time_min(lec_start)
        lec_end_min = parse_time_min(lec_end)
        if lec_start_min is None or lec_end_min is None:
            logging.warning('Skipping existing lecture during conflict check due to invalid times: %r', lec)
            continue
        
        # overlapping days
        for d in days:
            if d in lec_days:
                # overlapping time
                if start_min < lec_end_min and lec_start_min < end_min:
                    return True  # Conflict detected
    return False  # No conflict
#####################################

# Settings helpers
def get_weekday_setting():
    """Return current weekday option: 'sun-thu' or 'mon-fri'. Defaults to 'sun-thu'."""
    if db is None:
        return 'sun-thu'
    try:
        doc = db.settings.find_one({'_id': 'global'})
        opt = (doc or {}).get('weekdays', 'sun-thu')
        return opt if opt in ('sun-thu', 'mon-fri') else 'sun-thu'
    except Exception as e:
        logging.warning('Failed to fetch settings: %s', e)
        return 'sun-thu'

def get_days_config():
    """Return (days list, day_map dict, rev_map dict) based on settings."""
    opt = get_weekday_setting()
    if opt == 'mon-fri':
        days = ['MON', 'TUE', 'WED', 'THU', 'FRI']
        day_map = {'1': 'MON', '2': 'TUE', '3': 'WED', '4': 'THU', '5': 'FRI'}
    else:
        days = ['SUN', 'MON', 'TUE', 'WED', 'THU']
        day_map = {'1': 'SUN', '2': 'MON', '3': 'TUE', '4': 'WED', '5': 'THU'}
    rev_map = {v: k for k, v in day_map.items()}
    return days, day_map, rev_map

app = Flask(__name__)
# Secret key
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'change-this-secret')

@app.route('/',methods=['GET', 'POST'])
@app.route('/index',methods=['GET', 'POST'])
def index():
    """Show classroom schedule."""
    classroom = request.args.get("classroom")
    if classroom is None:
        classroom = "1"  # Default to classroom 1 if not specified
    
    # Fetch all lectures for the selected classroom from MongoDB
    lectures = list(collection.find({"classroom": classroom}))
    
    # days/mappings from settings
    days, day_map, _ = get_days_config()
    # Time slots in 24-hour format (internal keys)
    times = ['08', '09', '10', '11', '12', '01', '02', '03', '04', '05', '06', '07']
    # Display times in 12-hour format with AM/PM
    display_times = ['8:00 AM', '9:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '1:00 PM', '2:00 PM', '3:00 PM', '4:00 PM', '5:00 PM', '6:00 PM', '7:00 PM']
    
    # empty schedule
    schedule = {day: {time: '' for time in times} for day in days}
    
    # fill schedule
    for lecture in lectures:
        course = lecture.get('course', '')
        instructor = lecture.get('instructor', '')
        days_str = lecture.get('days', '')  # String of day codes (e.g., '123' for SUN,MON,TUE)
        starttime = lecture.get('starttime', '00:00')
        endtime = lecture.get('endtime', '00:00')
        
        # extract hour
        start_hour = int(starttime.split(':')[0])
        end_hour = int(endtime.split(':')[0])
        
        # normalize hours
        if start_hour < 8:
            start_hour += 12
        if end_hour < 8:
            end_hour += 12
        
        # covered slots
        time_slots = []
        for h in range(start_hour, end_hour):
            if h <= 12:
                time_slots.append(f"{h:02d}")
            else:
                time_slots.append(f"{h-12:02d}")
        
        # assign to days/slots
        for d in days_str:
            day_name = day_map.get(d)
            if day_name and day_name in days:
                for t in time_slots:
                    if t in times:
                        schedule[day_name][t] = f"{course} - {instructor}"
    
    # render
    is_logged_in = bool(session.get('user'))
    return render_template('index.html', classroom=classroom, days=days, day_map=day_map, times=times, display_times=display_times, schedule=schedule, show_classroom_tabs=True, is_logged_in=is_logged_in)

@app.route('/cpanel')
def process():
    """Control panel."""
    # Provide current weekday option to cpanel
    return render_template('cpanel.html', show_classroom_tabs=False, weekday_option=get_weekday_setting())


@app.route('/change_password', methods=['POST'])
def change_password():
    """Change password."""
    if not session.get('user'):
        return redirect(url_for('login', next=url_for('process')))

    username = session.get('user')
    current = request.form.get('current_password')
    new = request.form.get('new_password')
    confirm = request.form.get('confirm_password')

    if not current or not new or not confirm:
        return render_template('cpanel.html', show_classroom_tabs=False, error='All fields are required')
    if new != confirm:
        return render_template('cpanel.html', show_classroom_tabs=False, error='New passwords do not match')
    if collection is None:
        return render_template('cpanel.html', show_classroom_tabs=False, error='Database not configured')

    try:
        user_doc = db.users.find_one({'username': username})
    except Exception as e:
        logging.error('DB error fetching user: %s', e)
        return render_template('cpanel.html', show_classroom_tabs=False, error='Database error')

    if not user_doc:
        return render_template('cpanel.html', show_classroom_tabs=False, error='User not found')
    if user_doc.get('password') != current:
        return render_template('cpanel.html', show_classroom_tabs=False, error='Current password incorrect')

    # update password (note: plaintext storage—consider hashing in future)
    try:
        db.users.update_one({'username': username}, {'$set': {'password': new}})
        return render_template('cpanel.html', show_classroom_tabs=False, success='Password updated successfully')
    except Exception as e:
        logging.error('DB error updating password: %s', e)
        return render_template('cpanel.html', show_classroom_tabs=False, error='Failed to update password')


@app.route('/get_lecture')
def get_lecture():
    """Return lecture covering classroom/day/time."""
    classroom = request.args.get('classroom')
    day = request.args.get('day')
    time_key = request.args.get('time')
    if not classroom or not day or not time_key:
        return jsonify({})

    # day name → code
    _, _, rev_map = get_days_config()
    day_code = rev_map.get(day)
    if not day_code:
        return jsonify({})

    # convert time key to minutes for comparison
    try:
        t_h = int(time_key)
    except Exception:
        return jsonify({})

    # Find candidate lectures in this classroom that include the day
    candidates = list(collection.find({"classroom": classroom}))
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


@app.route('/lectures')
def lectures_for_classroom():
    """List lectures for a classroom (JSON)."""
    classroom = request.args.get('classroom')
    if not classroom:
        return jsonify({'lectures': []})
    docs = list(collection.find({'classroom': classroom}))
    out = []
    for d in docs:
        o = {k: v for k, v in d.items() if k != '_id'}
        o['_id'] = str(d['_id'])
        out.append(o)
    return jsonify({'lectures': out})


@app.route('/update_lecture', methods=['GET', 'POST'])
def update_lecture():
    """Update a lecture by id."""
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
    classroom = request.args.get('classroom') or request.form.get('classroom')
    instructor = request.args.get('instructor') or request.form.get('instructor')

    # minimal validation
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
        'classroom': classroom,
        'instructor': instructor,
    }
    collection.update_one({'_id': oid}, {'$set': update})
    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        update_out = update.copy()
        update_out['_id'] = str(oid)
        return jsonify({'success': True, 'lecture': update_out})

    # redirect back
    try:
        target_classroom = classroom if classroom else '1'
    except Exception:
        target_classroom = '1'
    return redirect(f"/index?classroom={target_classroom}")

@app.route('/about')
def about():
    """About page."""
    return render_template('about.html', show_classroom_tabs=False)


@app.route('/update_settings', methods=['POST'])
def update_settings():
    """Update global weekday option (requires login)."""
    if not session.get('user'):
        return redirect(url_for('login', next=url_for('process')))

    option = request.form.get('weekday_option')
    if option not in ('sun-thu', 'mon-fri'):
        return render_template('cpanel.html', show_classroom_tabs=False, weekday_option=get_weekday_setting(), error='Invalid option')
    try:
        db.settings.update_one({'_id': 'global'}, {'$set': {'weekdays': option}}, upsert=True)
        return render_template('cpanel.html', show_classroom_tabs=False, weekday_option=option, success='Settings updated')
    except Exception as e:
        logging.error('DB error updating settings: %s', e)
        return render_template('cpanel.html', show_classroom_tabs=False, weekday_option=get_weekday_setting(), error='Failed to update settings')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', show_classroom_tabs=False)

    # POST: authenticate
    username = request.form.get('username')
    password = request.form.get('password')
    next_url = request.args.get('next') or request.form.get('next') or url_for('index')
    
    # Validate input fields
    if not username or not password:
        return render_template('login.html', show_classroom_tabs=False, error='Please enter both username and password')
    
    user_found = db.users.find_one({"username": username})

    if user_found:
        # 2. Get the stored password (assuming it's stored as string)
        password_from_db = user_found.get('password')
        if password_from_db == password:
            session['user'] = username
            return redirect(next_url) # "Login successful!"
        else:
            return render_template('login.html', show_classroom_tabs=False, error='Incorrect password. Please try again.')
    else:
        return render_template('login.html', show_classroom_tabs=False, error='User not found. Please check your username.')


@app.route('/logout')
def logout():
    session.pop('user', None)
    # redirect back to home or referer
    ref = request.headers.get('Referer')
    if ref:
        return redirect(ref)
    return redirect(url_for('index'))

@app.route('/insert_lecture', methods=['GET', 'POST']) #allow both GET and POST requests
def insert_lecture():
    """Insert a new lecture."""
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
    classroom = request.args.get("classroom") or request.form.get("classroom")
    instructor = request.args.get("instructor") or request.form.get("instructor")

    # minimal validation
    if not starttime or not endtime:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'starttime and endtime required'}), 400
        return 'starttime and endtime required', 400
    
    # lecture doc
    lecture = {
    "course" : course,
    "days" : days,
    "starttime" : starttime,
    "endtime" : endtime,
    "numberOfStudents" : numberOfStudents,
    "classroom" : classroom,
    "instructor" : instructor
    }

    # conflict check
    if has_conflict(lecture):
        return '''<html>
                  <body>
                  <h1>Conflict detected: Classroom is not free during this time slot</h1>
                      <a href="/index">Home Page</a> |
                      <a href="/cpanel">Add lecture</a>
                  </body>
                  </html>'''

    # insert
    result = collection.insert_one(lecture)

    # AJAX response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        lecture_out = lecture.copy()
        lecture_out['_id'] = str(result.inserted_id)
        return jsonify({'success': True, 'lecture': lecture_out})

    # redirect back
    target_classroom = classroom if classroom else '1'
    return redirect(f"/index?classroom={target_classroom}")
# Run app
if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Run app in debug mode on port 5000
