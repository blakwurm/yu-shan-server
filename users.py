from auth import requires_auth
from data import addRows, readRows, modifyRows, deleteRow, buildResponse
simple_return = {"resp": 0, "data": [], "error": ""}

__tablename = 'users'

@requires_auth
def remove(apikey, body):
    return buildResponse(deleteRow(__tablename, body))

@requires_auth
def new(apikey): 
    return buildResponse(addRows(__tablename, body))

@requires_auth
def reset(apikey, body):
    return buildResponse(modifyRows(__tablename, body))

@requires_auth
def check(apikey):
    args = locals()
    result = readRows(__tablename, args)
    return buildResponse(result)