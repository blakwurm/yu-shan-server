from auth import requires_auth
from data import addRows, readRows, modifyRows, deleteRow, buildResponse
simple_return = {"resp": 0, "data": [], "error": ""}

__tablename = 'entities'

@requires_auth
def remove(apikey, body):
    return buildResponse(deleteRow('entities', body))

@requires_auth
def add(apikey, body): 
    return buildResponse(addRows(__tablename, body))

@requires_auth
def modify(apikey, body):
    return buildResponse(modifyRows('entities', body))

def read(apikey, id=None, category=None, name=None, description=None, count=None, page=None, method='and'):
    result = readRows(__tablename,
    {
        'id': id,
        'name': name,
        'description': description,
        'count': count,
        'page': page,
        'method': method
    })
    return buildResponse(result)