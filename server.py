# Getting the data from process.html form then
# inserting data in MongoDB labsDB database

from pymongo import MongoClient
# connecting to the database (with auth user:Samy password:asd123)
try:
    client = MongoClient('mongodb://samy:asd123@localhost:27017/labsDB?authSource=labsDB')
    print("Connected successfully!!!")
except:
	print("Could not connect to MongoDB")

# database
db = client.labsDB

# convert into mongoDB document object
collection = db.lectures

# load the full database into cursor
cursor = collection.find()
# for record in cursor:
# 	print(record)

#####################################
######### GOODIES ###################
#split a string into list of characters
def split(word):
    return [char for char in word]
#####################################

#starting coding the Flask app
from flask import Flask, request, redirect, render_template


labapp = Flask(__name__) #create the Flask app

@lapapp.route('/',methods=['GET', 'POST'])
@labapp.route('/index',methods=['GET', 'POST'])
def index():
    lab = request.args.get("lab")
    if lab == None:
        lab = "1"
    return render_template('index.html',lab=lab)

@labapp.route('/test',methods=['GET', 'POST'])
def test():
    labx = request.args.get("lab")
    cursor = collection.find({"lab":str(labx)}) #get lab X
    cursor.sort('starttime')  #sort by day then by start time
    user = {'username':'Samy','role':'admin'}
    title = "this is a test for flask usage"
    return render_template('testing.html',lab=labx,title=title,user=user,cursor=cursor)

@labapp.route('/cpanel')
def process():
    return render_template('cpanel.html')

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

    # Insert Data
    lecture_id = collection.insert_one(lecture)
    #
    # print("Data inserted successfully")
    # course = request.form('course')
    # print(course)
    return '''<html>
              <body>
              <h1>Lecture submitted with ID {{lecture_id}}</h1>
                  <a href="/index">Home Page</a> |
                  <a href="/cpanel">Add lecture</a>
              </body>
              </html>'''
#run the flask app
if __name__ == '__main__':
    labapp.run(debug=True,port=5000) #run app in debug mode on port 5000
