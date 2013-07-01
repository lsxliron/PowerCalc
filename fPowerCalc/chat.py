from socket import *
from subprocess import call
import re
import database
import sys
from database import Client as Client
from database import Software as Software



def main():
	#Get database session and engine
	engine = database.get_engine()
	session = database.get_session()


	HOST = '192.168.1.33' #The server IP
	PORT = 9000	#PORT

	s = socket(AF_INET, SOCK_STREAM)# 98% of all socket programming will use AF_INET and SOCK_STREAM
	s.bind((HOST, PORT)) 
	s.listen(1) # how many connections it can receive at one time 
	conn, addr = s.accept() # accept the connection
	print (str(conn))
	print str(addr)

	print 'Connected by', addr # print the address of the person connected

	while True: 


		
		data = conn.recv(1024) #recives datae using conn and store into data print "Received ", 
		if (repr(data) == "''"):	
			conn, addr = s.accept()
		
		else:
			print repr(data) # print data; Data is the message the users types `

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
		
#______________________________________________________________________________________________________________
#										CLOSING CONNECTION
#______________________________________________________________________________________________________________		
		if (repr(data) == "'EOF'"):
			s.shutdown(0)
			s.close()

#______________________________________________________________________________________________________________
#										Clients Screenshots (UNIX ONLY)
#______________________________________________________________________________________________________________		

		#Takes a screenshot from the mac.
		#Need to change parameters as ip, users and libraries
		if (user_msg[0]=='snapshot'):
			client_name = user_msg[1]
			
			for client in session.query(Client).filter(Client.name == client_name):
				client_ip = client.IP
				client_pass = client.password
				client_username = client.username

			call (['sshpass','-p', client_pass,'ssh', client_username+'@'+client_ip, '/usr/local/bin/imagesnap','/Users/lsxliron/Desktop/temp.jpeg'])



			# call(['sshpass','-p','1qaz','ssh','lsxliron@192.168.1.14','/usr/local/bin/imagesnap','/Users/lsxliron/Desktop/temp.jpeg'])
			# call(['sshpass','-p','1qaz','scp','lsxliron@192.168.1.14:/Users/lsxliron/Desktop/temp.jpeg','/home/lsxliron/Desktop/temp.jpeg'])
			# call (['sshpass','-p','1qaz','ssh','lsxliron@192.168.1.14','rm','/Users/lsxliron/Desktop/temp.jpeg'])
			# call(["python", "/home/lsxliron/Desktop/sendEmail.py"])	

		
#______________________________________________________________________________________________________________
#										MATLAB COMMANDS
#______________________________________________________________________________________________________________

		
		
		if (user_msg[0] == 'Matlab'):	#Case user uses matlab
			#get client ip, username and password
			

			client_name = user_msg[1]

			#get client os
			client_os = database.get_client_os(client_name)



			for client in session.query(Client).filter(Client.name == client_name):
				client_ip = client.IP
				client_pass = client.password
				client_username = client.username



			#case that client doesnt exists
			if (client_ip == None or client_pass == None or client_username == None):
				conn.sendall ('Client does not exists in the system.')

			
				#find software path for this client
				for software in session.query(Software).filter(Software.client_name == client_name):
					sw_path = str(software.path)

				if (sw_path == None):
					conn.sendall("This software does not exists for this client")

				else:	#Execute matlab command	
					if (client_os == 'UNIX'):
						call(['sshpass','-p',client_pass,'ssh', client_username+'@'+client_ip, sw_path,'-nodesktop','-noawt','-nosplash','-r',"\"publish('test.m',struct('codeToEvaluate','" + ' '.join(map(str,user_msg[2:len(user_msg)]))+"','showCode',true,'outputDir','/Users/lsxliron/Desktop','format','pdf')),exit\""])

					else:
						call(['sshpass','-p',client_pass,'ssh', client_username+'@'+client_ip, sw_path,'-nodesktop','-noawt','-nosplash','-r',"\"publish('test.m',struct('codeToEvaluate','" + ' '.join(map(str,user_msg[2:len(user_msg)]))+"','showCode',true))\"",'exit'])



				
				

#______________________________________________________________________________________________________________
#												JUNK
#______________________________________________________________________________________________________________

		#Matlab Methods
		if (repr(data)== "'Matlab1'"):
			conn.sendall("Please enter the method name and arguments foo(a,b)\n")
			data=conn.recv(1024)
			func=re.findall(r'\'.*\'',repr(data))
			if (len(data) > 0):
				func = func[0]
				func = func[1:-1]
				print func + " PRINTED BY ME"
				eval(func)
				conn.sendall("Simulation successful, the published document was sent to your email.")
			#if (repr(data)=="''"):
			#	conn, addr = s.accept()

			if (repr(data) == "'test'"):
				print "!!!"
				testMethod(1,2)





			if (repr(data) == "'ssh'"):
				print "!!!!"
				sshtest(1,2)
				


def sshtest(a, b):
	call (['sshpass','-p','1qaz','ssh','lsxliron@192.168.1.32','/Applications/MATLAB_R2012a.app/bin/matlab','-noawt', '-nodesktop','-nosplash','-r', "\"publish('test.m',struct('codeToEvaluate','test("+str(a)+","+str(b)+")','showCode',true,'outputDir','/Users/lsxliron/Desktop','format','pdf')),exit\""])
	call (['sshpass','-p','1qaz','scp','lsxliron@192.168.1.32:/Users/lsxliron/Desktop/test.pdf','/home/lsxliron/Desktop/temp.pdf'])
	call (['sshpass','-p','1qaz','ssh','lsxliron@192.168.1.32','rm','/Users/lsxliron/Desktop/test.pdf'])
	call (['python',"/home/lsxliron/Desktop/1.py"])


def testMethod(a, b):
	call (['/Applications/MATLAB_R2012a.app/bin/matlab','-noawt', '-nodesktop','-nosplash','-r', "publish('test.m',struct('codeToEvaluate','test(1,2)','showCode',true,'outputDir','/Users/lsxliron/Desktop','format','pdf')),exit"])


#reply = raw_input("Reply: ") 
		#conn.sendall(reply)


if __name__ == '__main__':
	main()


