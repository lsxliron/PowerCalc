from django.utils import simplejson
from dajaxice.decorators import dajaxice_register

@dajaxice_register(method="POST")
def sayhello (request, clientName, clientUsername, clientPassword, clientIP, clientPort, clientOS):
	
	print clientName
	print clientUsername
	print clientPassword
	print clientIP
	print clientPort
	print clientOS
	
	return simplejson.dumps({'message':'Hello World','test':clientOS})

