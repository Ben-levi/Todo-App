# bolilerplate for flask app
from flask import Flask, render_template, request, redirect , url_for
from dotenv import load_dotenv
from prometheus_flask_exporter import PrometheusMetrics
import logging
logging.basicConfig(level=logging.DEBUG)
import os
load_dotenv()


db_to_use = os.getenv("DATABASE_TYPE", "MYSQL")

from data_sql import (get_tasks, create_task, delete_task, 
						findByNumber, update_task, search_task, 
						check_task_exist)



app = Flask(__name__)
metrics = PrometheusMetrics(app)

##################################################################
########## ROUTES ################################################
##################################################################

@app.route('/')
def welcome():
    return render_template('welcome.html')


@app.route('/addtask')
def addtask():
    return render_template('addtasksForm.html')


@app.route('/createtask', methods=['POST'])
def createtask():
	fullname = request.form['fullname']
	priorty = request.form['priorty']
	Status = request.form['Status']
	person = request.form['person']
	photo = request.files['photo']
	if not check_task_exist(fullname):			
		if photo:
			file_path = 'HWFLASK/static/images/' + fullname + '.png'   
			photo.save(file_path)   
	
		create_task(fullname,priorty,Status,person, f'{fullname}.png')
		return redirect('/viewtasks')
	else: 
		return render_template('addtasksForm.html', message = 'task already exists')
 

@app.route('/viewtasks')
def viewtasks():
    return render_template('tasksTable.html' , tasks = get_tasks())



@app.route('/deletetask/<number>')
def deletetask(number): 
	delete_task(number)
	return redirect('/viewtasks')

@app.route('/edittask/<int:number>')
def edittask(number):
    try:
        task = findByNumber(number)
        if task:
            return render_template('edittaskForm.html', task=task)
        else:
            logging.debug(f"task with number {number} not found.")
            return render_template('error.html', message="task not found"), 404
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return render_template('error.html', message=f"An error occurred: {str(e)}"), 500




@app.route('/search', methods=['POST'])
def search():
	task_name = request.form['search_name']
	filtered_tasks = search_task(task_name)
	return render_template('tasksTable.html', tasks = filtered_tasks)
   


@app.route('/saveUpdatedtask/<number>', methods=['POST'])
def saveUpdatedtask(number):
    try:
        fullname = request.form['fullname']
        priorty = request.form['priorty']
        Status = request.form['Status']
        person = request.form['person']
        
        app.logger.debug(f"Received data - Name: {fullname}, Priority: {priorty}, Status: {Status}, Person: {person}")
        
        update_task(number, fullname, priorty, Status, person)
        return redirect(url_for('viewtasks'))
    except Exception as e:
        app.logger.error(f"Error updating task: {str(e)}")
        return render_template('error.html', message="An error occurred while updating the task"), 500



if __name__ == '__main__':
    app.run(port=5000)