from auth import requires_auth
from data import addRows, readRows, buildResponse
simple_return = {"resp": 0, "data": [], "error": ""}

__tablename = 'relationships'
@requires_auth
def remove(apikey, body):
    return simple_return

@requires_auth
def add(apikey, body): 
    return buildResponse(addRows(__tablename, body))

@requires_auth
def modify(apikey, body):
    return simple_return

def read(apikey, id=None, description=None, owner=None, _property=None, count=None, page=None, method='and'):
    result = readRows(__tablename,
    {
        'id': id,
        'owner': owner,
        'property': _property,
        'description': description,
        'count': count,
        'page': page,
        'method': method
    })
    return buildResponse(result)