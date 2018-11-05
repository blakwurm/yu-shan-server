from auth import requires_auth, makeNewUser
import auth
from data import addRows, readRows, modifyRows, deleteRow, buildResponse
import data
simple_return = {"resp": 0, "data": [], "error": ""}

__tablename = 'users'

@requires_auth
def remove(apikey, body):
    return buildResponse(deleteRow(__tablename, body))

def new(apikey): 
    email = auth.getProvidedUsername()
    password = auth.getProvidedPassword()
    errors = {False: (9, 'User Already Exists')}
    return buildResponse(makeNewUser(email = email, newpass = password), errors = errors)

@requires_auth
def reset(apikey, newpassword):
    return data.non_imp_response

@requires_auth
def check(apikey):
    args = locals()
    result = auth.getIDforEmail(auth.getProvidedUsername())
    return buildResponse(result)