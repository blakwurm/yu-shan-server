from auth import requires_auth, getCurrentUser
from data import addRows, readRows, modifyRows, deleteRow, buildResponse
simple_return = {"resp": 0, "data": [], "error": ""}

__tablename = 'relationships'
@requires_auth
def remove(apikey, body):
    return buildResponse(deleteRow('entities', body))

@requires_auth
def add(apikey, body): 
    currentUser = getCurrentUser()
    print('current user is {cu}'.format(cu = currentUser) )
    for thing in body:
        thing.update({'user': currentUser})
    print('body is {a}'.format(a=body))
    return buildResponse(addRows(__tablename, body))

@requires_auth
def modify(apikey, body):
    return buildResponse(modifyRows('relationships', body))

def read(apikey, id='*', description=None, owner=None, _property=None, count=None, page=None, method='and'):
    args = locals()
    result = readRows(__tablename, args)
    return buildResponse(result)