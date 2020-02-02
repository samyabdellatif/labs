# Getting the data from process.html form then
# inserting data in MongoDB labsDB database
from flask import Flask, request, redirect, render_template
from pymongo import MongoClient

app = Flask(__name__) #create the Flask app

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/process')
def process():
    return render_template('process.html')

@app.route('/insert_lecture', methods=['GET', 'POST']) #allow both GET and POST requests
def insert_lecture():
    # course = request.form('course')
    # print(course)
    return '''<h1>Lecture submitted</h1>
                  <a href="index.html">Home Page</a> |
                  <a href="process.html">Add lecture</a>'''
#run the flask app
if __name__ == '__main__':
    app.run(debug=True,port=5000) #run app in debug mode on port 5000

# connecting to the database (with auth user:Samy password:asd123)
try:
    client = MongoClient('mongodb://samy:asd123@localhost:27017/labsDB?authSource=labsDB')
    print("Connected successfully!!!")
except:
	print("Could not connect to MongoDB")

# database
db = client.labsDB

# get lecture input
#course = input ("Course: ")

# number of elemetns as input
# n = int(input("number of days: "))
# # iterating till the range
# days = []
# for i in range(0, n):
#     num = int(input("Day"+str(i)+": "))
#     days.append(num) # adding the day
#
# starttime = input ("Start Time (eg, 1:00): ")
# endtime = input ("End Time (eg, 1:50): ")
# numberOfStudents = input ("Number of Students: ")
# lab = input ("Lab Number: ")
# instructor = input ("instructor: ")

# convert into mongoDB document object
collection = db.lectures
# lecture = {
#  	"course" : course,
#  	"days" : days,
#  	"starttime" : starttime,
#  	"endtime" : endtime,
#  	"numberOfStudents" : numberOfStudents,
#  	"lab" : lab,
#  	"instructor" : instructor
#     }
#

# Insert Data
#lecture_id = collection.insert_one(lecture)
#
# print("Data inserted successfully")

# Printing the data inserted
cursor = collection.find()
for record in cursor:
	print(record)
