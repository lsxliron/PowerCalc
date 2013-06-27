from flask import Flask, render_template, url_for, jsonify, request
from flask.ext.sqlalchemy import SQLAlchemy
import re
import database
import os


app = Flask(__name__)


@app.route('/')
def index():
	database.create_db_if_not_exists()
	return render_template("index.html")


@app.route('/pc_man/')
def config():
	clients_dict = dict(zip(database.get_clients(),database.get_clients_and_ip()))
	return render_template('pc_man.html',clients = clients_dict)


@app.route("/_pc_man/", methods=['POST'])
def add_client_to_db():

	clientName = str(request.form['clientName'])
	clientUsername = str(request.form['clientUsername'])
	clientPassword = str(request.form['clientPassword'])
	clientIP = str(request.form['clientIP'])
	clientPort = str(request.form['clientPort'])
	clientOS = str(request.form['clientOS'])
	
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
		if not (clientPort > 0 and clientPort < 65535):
			raise Exception
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

@app.route('/_pc_man_sw/')
def config1():
	client = request.args.get('clientName','',type=str)
	os = database.get_client_os(client)
	return jsonify(os = os)

@app.route('/_pc_man_add_sw/', methods=['POST'])
def add_software_to_db():
	software_name = str(request.form['softwareName'])
	client_name = str(request.form['clientName'])
	software_path = str(request.form['softwarePath'])

	err_msg = ''
	os = database.get_client_os(client_name)

	if (os == 'WINDOWS'):
		software_path = "matlab"

	res = database.add_software_to_database(software_name, client_name, software_path)

	if (res == 1): #FAILIURE
		err_msg = 'Software already exists for this client'

	return jsonify(err_msg = err_msg)



if __name__ == '__main__':
	app.run(debug=True)