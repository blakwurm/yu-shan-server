from auth import requires_auth 
import auth
from data import addRows, readRows, modifyRows, deleteRow, buildResponse
simple_return = {"resp": 0, "data": [], "error": ""}

__tablename = 'entities'

@requires_auth
def remove(apikey, body):
    return buildResponse(deleteRow(__tablename, body))

@requires_auth
def add(apikey, body): 
    additions = addRows(__tablename, body)
    userID = auth.getIDforEmail(auth.getProvidedUsername())
    [auth.claimEntity(userID, x) for x in additions]
    return buildResponse(additions)

@requires_auth
def modify(apikey, body):
    canmodify = [auth.canUserModifyEntity(auth.getProvidedUsername, x['id']) for x in body]
    return buildResponse(modifyRows(__tablename, body))

def read(apikey, id='*', category=None, name=None, description=None, count=10, page=1, method='and'):
    args = locals()
    result = readRows(__tablename, args)
    return buildResponse(result)