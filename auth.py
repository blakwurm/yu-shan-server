'''
Connexion HTTP Basic Auth example
Most of the code stolen from http://flask.pocoo.org/snippets/8/
Warning: It is recommended to use 'decorator' package to create decorators for
         your view functions to keep Connexion working as expected. For more
         details please check: https://github.com/zalando/connexion/issues/142
'''

import connexion
import flask
from data import addRows, readRows, buildResponse, connection, connector

try:
    from decorator import decorator
except ImportError:
    import sys
    import logging
    logging.error('Missing dependency. Please run `pip install decorator`')
    sys.exit(1)


def check_auth(username: str, password: str):
    '''This function is called to check if a username /
    password combination is valid.'''
    currentUser = getCurrentUser()
    print('username is ' + username + ' and password is ' + password)
    return username == 'admin@yu-shan.com' and password == 'secret'


def authenticate():
    '''Sends a 401 response that enables basic auth'''
    # return flask.Response('You have to login with proper credentials', 401,
    #                       {'WWW-Authenticate': 'Basic realm="Login Required"'})
    return {'resp': 10, 'data': [], 'error': 'Not authenticated'}


@decorator
def requires_auth(f: callable, *args, **kwargs):
    auth = flask.request.authorization
    if not auth or not check_auth(auth.username, auth.password):
        return authenticate()
    return f(*args, **kwargs)

@connector
def getCurrentUser(c):
    auth = flask.request.authorization
    logged_in = check_auth(auth.username, auth.password)
    return getIDforEmail(auth.username) if logged_in else ''

@connector
def getIDforEmail(email, c):
    if email:
        querystring = 'SELECT id FROM users WHERE email = ?'
        return c.execute(querystring, [email]).fetchone()[0]
    else:
        return  ''


@connector
def getUserData(*, userID = '', email = '', c):
    the_id = userID if userID else getIDforEmail(email)
    if the_id:
        userOb = c.execute('SELECT * FROM users WHERE id = ?', [userID]).fetchone()
        entityOb = c.execute('SELECT * FROM entities WHERE id = ?', [userID]).fetchone()
        user = readRows('users', {'id': userID})[0]
        entity = readRows('entities', {'id': userID})[0]
        return (user, entity)
    return ('', '')

@connector
def makeNewUser(email, c):
    user, entity = getUserData(getCurrentUser())