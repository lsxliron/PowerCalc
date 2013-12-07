from socket import *
from subprocess import call
import re
import database
import sys
import os
from database import Client as Client
from database import Software as Software
from sendEmaily import send_mail, getInfo
import time


def main():
	#GET DATABASE SESSION AND ENGINE
	engine = database.get_engine()
	session = database.get_session()
	
	#SET VARIABLES
	dataList = getInfo()
	HOST = dataList[2] #The server IP
	PORT = int(dataList[3]) #PORT
	
	#CONNECTION SETUP
	s = socket(AF_INET, SOCK_STREAM)
	s.bind((HOST, PORT)) 
	s.listen(1) 
	conn, addr = s.accept() 
	print (str(conn))
	print str(addr)

	#PRINT ADDRESS OF CONNECTED DEVICE
	print 'Connected by', addr 

	while True: 
		

		data = conn.recv(1024) 
		if (repr(data) == "''"):	
			conn, addr = s.accept()
		
		#PRINT MESSAGES TO THE DISPLAY
		else:
			print repr(data) 

		##VARIABLES:
		client_ip = ''
		client_pass = ''
		client_username = ''
		sw_path = ''
		client_os = ''


		#CONVERTING USER MESSAGE TO A LIST
		temp_user_msg = repr(data)
		temp_user_msg = temp_user_msg[1:-1]
		user_msg = temp_user_msg.split(' ')
		
		if (user_msg[0] == 'Matlab'):
			function = user_msg[2]
			function = re.findall(".*?\(", function)
			function = function[0][:-1]
			print function
#______________________________________________________________________________________________________________
#					CLOSING CONNECTION
#______________________________________________________________________________________________________________		
		if (repr(data) == "'eof'"):
			s.shutdown(0)
			s.close()

#______________________________________________________________________________________________________________
#				Clients Screenshots 
#______________________________________________________________________________________________________________		

		#Takes a screenshot from the mac.
		if (user_msg[0]=='snapshot'):
			client_name = user_msg[1]
			
			for client in session.query(Client).filter(Client.name == client_name):
				client_ip = client.IP
				client_pass = client.password
				client_username = client.username
				client_os = client.OS
			
			#CASE CLIENT IS MACOS
			if (client_os == 'UNIX'):
				conn.sendall('A snapshot from you computer webcam will be sent to your email soon.\n\n')
				print "DEBUG: TAKING SNAPSHOT"
				call (['sshpass','-p', client_pass, 'ssh', client_username + '@' + client_ip, '/usr/local/bin/imagesnap', '/Users/' + client_username  + '/Desktop/snap.jpeg'])

				print 'DEBUG: COPYING SNAPSHOT FROM CLIENT TO SERVER'
				call (['sshpass','-p', client_pass, 'scp', client_username + '@' + client_ip + ':/Users/' + client_username + '/Desktop/snap.jpeg', os.getenv('HOME') + '/PowerCalcTempFiles/snap.jpeg'])

				print 'DEBUG: SENDING SNAPSHOT TO EMAIL'
				send_mail('Your snapshot from ' + client_name, '<h3>This picture was taken from your computer.</h3><h4><b>Produced by PowerCalc</b></h4>','python',1)

				print 'DELETING FILE FROM CLIENT'
				call (['sshpass','-p', client_pass, 'ssh', client_username + '@' + client_ip, 'rm', '/Users/' + client_username + '/Desktop/snap.jpeg'])

				print 'DEBUG: COMPLETE.\n\n SERVER IS NOW READY.\n\n'

			#CASE CLIENT IS WINDOWS	
			elif (client_os == "WINDOWS"):
				
				conn.sendall('A snapshot from you computer webcam will be sent to your email soon.\n\n')
				print "DEBUG: TAKING SNAPSHOT"
				call (['sshpass','-p', client_pass, 'ssh', client_username + '@' + client_ip, 'CommandCam /filename C:\\PCTemp\\snap.jpeg'])
				time.sleep(5)
				print 'DEBUG: COPYING SNAPSHOT FROM CLIENT TO SERVER'
				call (['sshpass', '-p', client_pass, 'sftp', client_username + '@' + client_ip + ':snap.jpeg', os.getenv('HOME') + '/PowerCalcTempFiles/snap.jpeg'])
				
				print 'DEBUG: SENDING SNAPSHOT TO EMAIL'
				send_mail('Your snapshot from ' + client_name, '<h3>This picture was taken from your computer.</h3><h4><b>Produced by PowerCalc</b></h4>','python',1)

				print 'DELETING FILE FROM CLIENT'
				call (['sshpass','-p', client_pass, 'ssh', client_username + '@' + client_ip, 'del snap.jpeg'])

				print 'DEBUG: COMPLETE.\n\n SERVER IS NOW READY.\n\n'


#______________________________________________________________________________________________________________
#						MATLAB COMMANDS
#______________________________________________________________________________________________________________

		
		
		if (user_msg[0] == 'Matlab'):	
			
			#GET CLIENT USER, IP AND PASSWORD
			client_name = user_msg[1]

			#GET CLIENT OS
			client_os = database.get_client_os(client_name)



			for client in session.query(Client).filter(Client.name == client_name):
				client_ip = client.IP
				client_pass = client.password
				client_username = client.username



			#CASE THAT CLIENT DOES NOT EXISTS
			if (client_ip == None or client_pass == None or client_username == None):
				conn.sendall ('Client does not exists in the system.')


			#FIND SOFTWARE PATH FOR CLIENT
			for software in session.query(Software).filter(Software.client_name == client_name):
				sw_path = str(software.path)
			print "______________________________"
		        print "CLIENT DETAILS:"
			print client_name
			print client_username
			print client_pass
			print client_os
			print sw_path
			print "______________________________"


			if (sw_path == None):
				conn.sendall("This software does not exists for this client")

			else:	#Execute matlab command
				conn.sendall("Processing calculation.\nThe published document will be sent to your email.\n")
		
				if (client_os == 'UNIX'):
					print "______________UNIX MATLAB CALL______________"
					print "DEBUG: EXECUTING FUNCTION:"
					print ' '.join(map(str,user_msg[2:len(user_msg)]))
					call(['sshpass','-p',client_pass,'ssh', '-X', client_username+'@'+client_ip, sw_path, '-nodesktop','-r',"\"publish('/Users/" + client_username + "/Documents/MATLAB/" + function  + ".m',struct('codeToEvaluate','" + ' '.join(map(str,user_msg[2:len(user_msg)]))+"','showCode',true,'outputDir','/Users/" + client_username + "/Documents/MATLAB','format','pdf')),exit\""])

					print "DEBUG: COPYING PUBLISHED FILE FROM CLIENT TO SERVER"                                        					
					call(['sshpass','-p', client_pass, 'scp',client_username+'@'+client_ip+':/Users/' + client_username + '/Documents/MATLAB/'+function+'.pdf',os.getenv('HOME') + '/PowerCalcTempFiles/temp.pdf'])
					
					print "DEBUG: SENDING EMAIL TO USER"
					send_mail('Your results for '+function,'<h2>The attached file is your Matlab published file</h2><br><h4>Produced by PowerCalc</h4>','python')
					
					print "DEBUG: REMOVING FILE FROM CLIENT"
					call(['rm','-f', os.getenv('HOME') + '/PowerCalcTempFiles/temp.pdf'])
					

					print "DEBUG: COMPLETE!\n\nSERVER READY\n\n"


				else:
					print "______________WINDOWS MATLAB CALL______________"
					print "DEBUG: CALLING FOR FUNCTION:"
					print ' '.join(map(str,user_msg[2:len(user_msg)]))
					
					call(['sshpass', '-p', client_pass, 'ssh', client_username + '@' + client_ip, 'matlab', '-nodesktop', '-r', "\"publish('"+function+".m', struct('codeToEvaluate', '" + ' '.join(map(str,user_msg[2:len(user_msg)])) + "','outputDir','C:\\PCTemp','format','pdf')), exit;\""])
					print "CONNETCED TO CLIENT"
					while not os.path.isfile(os.getenv('HOME') + '/PowerCalcTempFiles/temp.pdf'):
						call(['sshpass','-p', client_pass,'sftp',client_username+'@'+client_ip+':'+function+'.pdf',os.getenv('HOME') + '/PowerCalcTempFiles/temp.pdf'])
						time.sleep(30)
	
					call(['sshpass','-p', client_pass, 'ssh',client_username + '@' + client_ip, 'cmd /c  del /Q C:\\PCTemp\\test.pdf'])
					
					print "DEBUG: SENDING EMAIL TO USER"
					send_mail('Your results for '+function,'<h2>The attached file is your Matlab published file</h2><br><h4>Produced by PowerCalc</h4>','python')
	
					print "DEBUG: REMOVING PUBLISHIED FILE FROM SERVER"
					call(['rm',os.getenv('HOME')+'/PowerCalcTempFiles/temp.pdf'])
					
					print "DEBUG: COMPLETE\n\nSERVER READY\n\n"
	


if __name__ == '__main__':
	main()


