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
from passlib.hash import pbkdf2_sha256 as hasher

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
    print('username is ' + username + ' and password is ' + password)
    existID = getIDforEmail(username)
    user, entity = getUserData(userID = existID)
    password = getProvidedPassword()
    return hasher.verify(password, user['check'])


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

def getProvidedUsername():
    return flask.request.authorization.username

def getProvidedPassword():
    return flask.request.authorization.password

@connector
def getIDforEmail(email, c):
    if email:
        querystring = 'SELECT id FROM users WHERE email = ?'
        res = c.execute(querystring, [email]).fetchone()
        print('id for {a} is {b}'.format(a=email, b=res))
        return res[0]  if res else ''
    else:
        return  ''


@connector
def getUserData(*, userID = '', c):
    if userID:
        userOb = c.execute('SELECT * FROM users WHERE id = ?', [userID]).fetchone()
        entityOb = c.execute('SELECT * FROM entities WHERE id = ?', [userID]).fetchone()
        user = readRows('users', {'id': userID})[0]
        entity = readRows('entities', {'id': userID})[0]
        return (user, entity)
    return ('', '')

@connector
def makeNewUser(email, newpass, c):
    existID = getIDforEmail(email)
    user, entity = getUserData(userID = existID)
    print('user is {a}'.format(a=user))
    if user:
        print('user exists, man')
        return False
    userID = addRows('entities', [{'category': 'player'}])[0]
    newuserob = {'email': email, 'id': userID, 'check': hasher.hash(newpass), 'verified': 0}
    addRows('users', [newuserob], genNewID=False)
    return userID

hashPass = hasher.hash

verifyPass = hasher.verify

@connector
def canUserModifyEntity(userID, entityID, c):
    # c.execute("SELECT * FROM relationships WHERE user = ? AND property = ?", [userID, entityID])
    thing = readRows('relationships', {'user': userID, 'property': entityID})
    return thing[0] if thing else False