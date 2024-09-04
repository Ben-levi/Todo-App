from pstats import Stats
import mysql.connector
import os
import logging
logging.basicConfig(level=logging.DEBUG)
from dotenv import load_dotenv
load_dotenv()



############## MYSQL Functions ####################


# Connect to MySQL database
db = mysql.connector.connect(
   host=os.getenv("DB_HOST", "localhost"),
   user=os.getenv("DB_USER", "root"),
   password=os.getenv("DB_PASSWORD", "admin"),
   port=os.getenv("DB_PORT", "3306"),
   )

def create_db():
   database=os.getenv("DB_NAME", "tasks_app")
   cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
   cursor.execute(f"USE {database}")
   db.commit()
   print(f"Database {database} created successfully")


def create_tasks_table():
	cursor.execute("Create Table IF NOT EXISTS tasks"
				   "(number INT AUTO_INCREMENT PRIMARY KEY,"
				   "fullname VARCHAR(255) not null,"
				   "priorty VARCHAR(255),"
				   "Status VARCHAR(255),"
				   "person VARCHAR(255),"
				   "photo VARCHAR(255))")
	db.commit()
	print("Table tasks created successfully")

cursor = db.cursor(dictionary=True)
# create database 
create_db()
# create tasks table
create_tasks_table()



def get_tasks():
   cursor.execute("SELECT * FROM tasks")
   result = cursor.fetchall()
   return result


# the function finds the contact by its number

def findByNumber(number):
    tasks_list = get_tasks()
    logging.debug(f"Tasks list: {tasks_list}")
    for task in tasks_list:
        logging.debug(f"Checking task: {task}")
        if task['number'] == number:
            return task
    return None

# the function checks if it exists by its name or email
def check_task_exist(fullname):
	cursor.execute("SELECT * FROM tasks WHERE fullname = %s", (fullname,))
	result = cursor.fetchone()
	return bool(result)


# function to search for the contact by its name
def search_task(fullname):
	cursor.execute("SELECT * FROM tasks WHERE fullname LIKE %s", ('%' + fullname + '%',))
	result = cursor.fetchall()
	return result


# create contact in the database
def create_task(fullname, priorty, Status, person, photo):
	cursor.execute("INSERT INTO tasks (fullname,priorty,Status,person,photo) VALUES (%s, %s, %s, %s, %s)", (fullname,priorty,Status,person, photo))
	db.commit()
	return f"task {fullname} added successfully"


# delete contact from the database
def delete_task(number):
	cursor.execute("DELETE FROM tasks WHERE number = %s", (number,))
	db.commit()
	return f"task {number} deleted successfully"


# update contact in the database
def update_task(number, fullname, priorty, Status, person):
   cursor.execute("UPDATE tasks SET fullname = %s, priorty = %s, Status = %s, person = %s WHERE number = %s",
                  (fullname, priorty, Status, person, number))
   db.commit()