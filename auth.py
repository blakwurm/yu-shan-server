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
    querystring = 'SELECT id FROM users WHERE email = ?'
    c.execute(querystring, [auth.username])
    return c.fetchone()[0] if logged_in else ''