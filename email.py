import smtplib
from contextlib import contextmanager

@contextmanager
def withEmail():
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.connect('smtp.gmail.com',  587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login('hahaha', 'hahaha')
    yield server

def testsend():
    server.sendmail('foo@yu-shan.com', 'achythlook@gmail.com', 'This is a message being sent from the server?')