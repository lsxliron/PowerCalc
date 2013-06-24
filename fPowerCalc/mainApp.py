from flask import Flask, render_template, url_for, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
import re
import database


app = Flask(__name__)


@app.route('/')
def index():
	database.create_db_if_not_exists()
	return render_template("index.html")


@app.route('/pc_man/')
def config():
	# url_for('static', filename='pc_man.css')
	return render_template('pc_man.html')


@app.route("/_pc_man/")
def add_client_to_db():
	clientName = request.args.get('clientName','',type=str)
	clientUsername = request.args.get('clientUsername','',type=str)
	clientPassword = request.args.get('clientPassword','',type=str)
	clientIP = request.args.get('clientIP','',type=str)
	clientPort = request.args.get('clientPort',type=int)
	clientOS = request.args.get('clientOS','',type=str)
	
	#Variables
	ip_valid = False	#for database enteries
	port_valid = False	#for database enteries
	ip_err_msg = ''
	port_err_msg = ''
	general_err = ''
	success_msg = '-1'
	
	'''
	Validate fields
	clientName, clientUsername,clientOS and clientPassword- doesn't need to be validated.
	

	validate IP
	'''
	valid_ip_address_regex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$"

	m = re.compile(valid_ip_address_regex)
	ip_checker = m.match(clientIP)
	
	if  ip_checker is not None:
		ip_valid = True	
	else:
		ip_err_msg = 'IP is not valid.\n'


	'''
	Validate port:
	'''
	try:
		clientPort = int(clientPort)
		port_valid = True

	except:
		port_err_msg = "Port is not valid."

	#Create insertion to database.
	if ip_valid and port_valid:
		insert = database.insert_client_to_database(clientName, clientUsername, clientPassword, clientIP, clientPort, clientOS)
		if insert == 1:
			general_err = 'The IP address you provided already in the database.'

	if ip_valid and port_valid and general_err=='':
		success_msg = 0
	#return back to jQuery
	return jsonify(clientName = clientName,
				   clientUsername = clientUsername,
				   clientPassword = clientPassword,
				   clientIP = clientIP,
				   clientPort = clientPort,
				   clientOS = clientOS,
				   ip_err_msg = ip_err_msg,
				   port_err_msg = port_err_msg,
				   general_err = general_err,
				   success_msg = success_msg
				   )




if __name__ == '__main__':
	app.run(debug=True)