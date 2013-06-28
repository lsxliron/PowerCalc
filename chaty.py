from socket import *
from subprocess import call
import re



def main():
	HOST = '172.20.10.9' #The server IP
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
		
		#Takes a screenshot from the mac.
		#Need to change parameters as ip, users and libraries
		if (repr(data)=="'mac'"):
			call(['sshpass','-p','1qaz','ssh','lsxliron@192.168.1.14','/usr/local/bin/imagesnap','/Users/lsxliron/Desktop/temp.jpeg'])
			call(['sshpass','-p','1qaz','scp','lsxliron@192.168.1.14:/Users/lsxliron/Desktop/temp.jpeg','/home/lsxliron/Desktop/temp.jpeg'])
			call (['sshpass','-p','1qaz','ssh','lsxliron@192.168.1.14','rm','/Users/lsxliron/Desktop/temp.jpeg'])
			call(["python", "/home/lsxliron/Desktop/sendEmail.py"])	
		if repr(data)=="'win'":
			call (['sshpass','-p','av2012','ssh','Jonathan@172.20.10.4', "matlab -nodesktop -nosplash -r \"publish('test.m',struct('codeToEvaluate','test(3,4)','showCode',true))\"",'exit'])
		#reply = raw_input("Reply: ") 
		#conn.sendall(reply)

		#Matlab Methods
		if (repr(data)== "'Matlab'"):
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



if __name__ == '__main__':
	main()


