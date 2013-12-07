import smtplib, os, re, sys, glob, string, datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
import email.Utils
from email import Encoders
from time import strftime, localtime


'''
GETS ALL THE INFO FROM fpc.conf
'''
def getInfo():
	currentDir = os.getenv('HOME')
	repo = "/Desktop/sp2test/sp1-nb/fPowerCalc"
	dataFile = open(currentDir + repo + '/fpc.conf','r')
	
	#GET USER DATA
	for line in dataFile.readlines():
	#FIND EMAIL
		if (len(re.findall("email=.*",line)) != 0): #EMAIL FOUND
			user_email = re.findall("=.*",line)	
			user_email = user_email[0][1:]
			
		if (len(re.findall("user_pass=.*",line)) != 0): #PASSWORD FOUND
			user_pass = re.findall("=.*",line)	
			user_pass = user_pass[0][1:]

		if (len(re.findall("IP=.*",line)) != 0): #IP FOUND
			server_IP = re.findall("=.*",line)	
			server_IP = server_IP[0][1:]
	
		if (len(re.findall("PORT=.*",line)) != 0): #PORT FOUND
			port = re.findall("=.*",line)	
			port = port[0][1:]

	data = [user_email, user_pass, server_IP, port]
	return data


'''
Reads the email body from external file and return it
'''
def getMessageBody():
	homeDir = os.getenv('HOME')
	dataFile = open(homeDir + '/PowerCalcTempFiles/tempData.txt')
	body = dataFile.readlines()
	body = ''.join(map(str,body))
	dataFile.close()
	return body

'''
Reads the email subject from external file and return it
'''
def getMessageSubject():
	homeDir = os.getenv('HOME')
	dataFile = open(homeDir + '/PowerCalcTempFiles/tempDataSubject.txt')
	subject = dataFile.readlines()
	subject = ''.join(map(str,subject))
	dataFile.close()
	return subject



#VARIABLES TO SETUP
def send_mail(subject, msg_body, lang='ruby', attachment=0):
    '''
    Sends email to a specific address
    '''

    #GET MESSAGE BODY FOR SIRIPROXY
    if (lang != 'python'):
        msg_body = getMessageBody()
	subject = getMessageSubject()
    
    dataList = getInfo()
    if (attachment == 0):
        attachmentname = os.getenv('HOME') + '/PowerCalcTempFiles/temp.pdf'  #PATH TO MATLAB PUBLISHED FILE
    elif (attachment == 1):
        attachmentname = os.getenv('HOME') + '/PowerCalcTempFiles/snap.jpeg' #PATH TO SNAPSHOT
    addr= dataList[0]
    username = dataList[0]
    password = dataList[1]
    
   

    fromaddr = '<'+ addr +'>'
    toaddr  = '<' + addr + '>'
    replyto = fromaddr          
    msgsubject = subject
    time  =  strftime("%b %d %Y at %H:%M:%S",localtime())
    htmlmsgtext = msg_body +'</br></br></br>' + time
    




    
    try:
        msgtext = htmlmsgtext.replace('<b>','').replace('</b>','').replace('<br>',"\r").replace('</br>',"\r").replace('<br/>',"\r").replace('</a>','')
        msgtext = re.sub('<.*?>','',msgtext)

        msg = MIMEMultipart()
        msg.preamble = 'This is a multi-part message in MIME format.\n'
        msg.epilogue = ''

        body = MIMEMultipart('alternative')
        body.attach(MIMEText(msgtext))
        body.attach(MIMEText(htmlmsgtext, 'html'))
        msg.attach(body)
    
        if attachmentname!=None and type(attachmentname) is str: #DO WE HAZ ATTACHMENT?
            f = attachmentname
            part = MIMEBase('application', "octet-stream")
            part.set_payload( open(f,"rb").read() )
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
            msg.attach(part)

    
        msg.add_header('From', fromaddr)
        msg.add_header('To', toaddr)
        msg.add_header('Subject', msgsubject)
        msg.add_header('Reply-To', replyto)
   
 
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.set_debuglevel(False) #commenting this out, changing to False will make the script give NO output at all upon successful completion
	
        server.starttls()
        server.login(username,password)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
    
        server.quit() 




    except:
        print ('Email NOT sent to %s successfully. %s ERR: %s %s %s ', str(toaddr), 'tete', str(sys.exc_info()[0]), str(sys.exc_info()[1]), str(sys.exc_info()[2]) )