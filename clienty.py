from socket import *
HOST = '172.20.10.9'
PORT = 9000
s = socket(AF_INET, SOCK_STREAM)
s.connect((HOST, PORT)) # client-side, connects to a host
while True:
	message = raw_input("Your Message: ")
	s.send(message)
	print "Awaiting reply"
	reply = s.recv(1024) # 1024 is max data that can be received
	print "Received ", repr(reply)
s.close()