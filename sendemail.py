import smtplib
from contextlib import contextmanager
import creds
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

emailusername, emailpassword = creds.getCredsFor('email')

@contextmanager
def emailConnection():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.connect('smtp.gmail.com',  587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(emailusername, emailpassword)
    yield server
    server.quit()

def testsend():
    with emailConnection() as server:
        server.sendmail('foo@yu-shan.com', 'achythlook@gmail.com', 'This is a message being sent from the server?')

def sendMessage(*, to, subject, body):
    with emailConnection() as server:
        msg = MIMEMultipart()
        msg['From'] = 'admin@yu-shan.com'
        msg['To'] = to
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        server.send_message(msg) 
        del msg
