#!/usr/bin/python
import MySQLdb
import datetime
import time
import os
import smtplib
from ftplib import FTP
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from contextlib import closing
from twilio.rest import TwilioRestClient
import traceback
#for ip address
import socket
#for shell execution
import subprocess

accountid = "YOUR TWILIO ACCOUNT"
token = "YOUR TWILIO TOKEN"
my_number = "YOUR TWILIO NUMBER"
recipients = ['RECIPIENTS OF THE EMAILS']
Sender = "YOUR EMAIL"
ID = "YOUR EMAIL ID"
password = "YOUR EMAIL PASSWORD"

#list of authorized phone number
authphone = []
#list of processed sid
sidlist = []

path = os.path

print 'The Path Is'
print os.getcwd()
#checking for the processed message id
if os.path.isfile(path.join('msgid')):
    print 'SID exist,fetching'
    sidfile = open(path.join('msgid'),'r')
    sidlist = sidfile.readlines()

#flag for first message
first_mess = True
#ip of this machine
try:
    ip = socket.gethostbyname(socket.gethostname())

    con = MySQLdb.connect('YOUR DOMAIN','USERNAME','PASS','DB')
# Twilio client which will be fetching messages from their server
    TwilioClient = TwilioRestClient(accountid,token)
except Exception:
    print traceback.format_exc()


#send email from gmail 
def SendGmail(to_send):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        starttls = server.starttls()
        login = server.login(ID,password)
        msg = MIMEMultipart()
        msg['Subject'] = "PassK: {0}".format(to_send)
        msg['From'] = From
        msg['To'] = ", ".join(recipients)
        sendit = server.sendmail(From, recipients, msg.as_string())
        server.quit()
    except Exception:
        print traceback.format_exc()



def msg_handler(msg):
    try:    
        print msg.body
        flag = False
        #if message got properly processed, change the flag so that
        #the rest of the message is discarded.save us some time
        #report on the last login
        if msg.body.lower() == 'login' and os.path.isfile(path.join('login')):
            text = open(path.join('login'),'r')
            line = text.read()
            SendGmail('PassK: Last Activity: {0}'.format(line))
            text.close()
        elif msg.body.lower() == 'request' and os.path.isfile(path.join('request')):
            text = open(path.join('request'),'r')
            SendGmail('PassK: Last Request: {0}'.format(text.read()))
            text.close()
        elif msg.body.lower()[:4] == 'pass':
            #write a new request file
            text = open(path.join('request'),'w')        
            text.write("phonenum {0} account {1} ddatetime {2} ipaddr {3}".format(msg.from_,msg.body[5:],time.strftime("'%Y-%m-%d %H:%M:%S'"), str(ip)))
	    text.flush()
	    text.close()
        else:
            mess = 'not valid message'
        first_mess = False
    except Exception:
        print traceback.format_exc()    

#fetching list of authorized phone from database
try:
    with closing(con.cursor()) as authorized_cursor:
        authorized_users = authorized_cursor.execute("select phonenum from authorized")
        auth_rows = authorized_cursor.fetchall()
        for auth_row in auth_rows:
            for auth_col in auth_row:
                authphone.append(auth_col)
except Exception:
    print traceback.format_exc()


#fetch all at once, not built for continuously processing message yet
try:
    #only process today's messages
    msgs = TwilioClient.messages.list(date_sent=datetime.datetime.utcnow())
    idlist = open(path.join('msgid'),'a')
    # we know that the smaller number messages is the later ones,
    # only process the first valid message
    for n in range(len(msgs)):
        p = msgs[n]
        Sender = p.from_
        # only process the messages come from the
        # fully received and authorized numbers
        # and it's the latest command from authroized user
        if p.status == 'received':
            #append the message id
            idlist.write(p.sid+'\n')
            if p.sid+'\n' not in sidlist:                    
                if p.from_ in authphone and first_mess:
                    msg_handler(p)
                    first_mess = False
    reqfile = open(path.join('request'),'r')
    req = reqfile.read()
    #get the acccount
    account = req.split()[3]
    #call the pass command
    p = subprocess.Popen(('pass', account), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    #create new payload
    payload = open(path.join('payload.dd'),'w')
    payload.write('STRING {0}'.format(stdout))
    #set chmod to only root can see
    subprocess.call(['chmod','700','payload.dd'])
    reqfile.close()
    payload.close()
    idlist.close()
except Exception:
    print traceback.format_exc()

