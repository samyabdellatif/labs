# Python code to illustrate
# inserting data in MongoDB
from pymongo import MongoClient

try:
    client = MongoClient('mongodb://samy:asd123@localhost:27017/labsDB?authSource=labsDB')
    print("Connected successfully!!!")
except:
	print("Could not connect to MongoDB")

# database
db = client.labsDB

# get lecture input
course = input ("Course: ")

# number of elemetns as input
n = int(input("number of days: "))
# iterating till the range
days = []
for i in range(0, n):
    num = int(input("Day"+str(i)+": "))
    days.append(num) # adding the day

starttime = input ("Start Time (eg, 1:00): ")
endtime = input ("End Time (eg, 1:50): ")
numberOfStudents = input ("Number of Students: ")
lab = input ("Lab Number: ")
instructor = input ("instructor: ")

# convert into mongoDB document object
collection = db.lectures
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

print("Data inserted successfully")

# Printing the data inserted
cursor = collection.find()
for record in cursor:
	print(record)
