import smtplib, os, re, sys, glob, string, datetime
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
import email.Utils
from email import Encoders
from time import strftime, localtime


#VARIABLES TO SETUP
def send_mail(addr, passwd, attch_name, subject, msg_body):
    '''
    Sends email to a specific address
    '''
    attachmentname =  attch_name #path to an attachment, if you wish
    username = addr
    password = passwd
    

    fromaddr = '<'+ addr +'>' #must be a vaild 'from' addy in your GApps account
    toaddr  = '<' + addr + '>'
    
    replyto = fromaddr          #unless you want a different reply-to

    msgsubject = subject

    time  =  strftime("%b %d %Y at %H:%M:%S",localtime())
    htmlmsgtext = msg_body +'</br></br></br>' + time
    #--------------------------------------------------------------------------------





    #ok,here goes nothing
    try:
        print email.Utils.parseaddr(username)
        msgtext = htmlmsgtext.replace('<b>','').replace('</b>','').replace('<br>',"\r").replace('</br>',"\r").replace('<br/>',"\r").replace('</a>','')
        msgtext = re.sub('<.*?>','',msgtext)

        #pain the ass mimey stuff
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
    ##msg.add_header('Cc', ccaddy)    #doesn't work apparently
    ##msg.add_header('Bcc', bccaddy)  #doesn't work apparently
        msg.add_header('Subject', msgsubject)
        msg.add_header('Reply-To', replyto)
    
    # The actual email sendy bits
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.set_debuglevel(True) #commenting this out, changing to False will make the script give NO output at all upon successful completion
        server.starttls()
        server.login(username,password)
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
    
        server.quit() #bye bye




    except:
        print ('Email NOT sent to %s successfully. %s ERR: %s %s %s ', str(toaddr), 'tete', str(sys.exc_info()[0]), str(sys.exc_info()[1]), str(sys.exc_info()[2]) )
   # #just in case
#send_mail('lsxliron@gmail.com','cxiualbosddgtjef','/home/lsxliron/Desktop/test22.pdf','EMAIL SUBJECT','BODY')
