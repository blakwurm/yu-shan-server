from auth import requires_auth
from data import addRow
simple_return = {"resp": 0, "data": [], "error": ""}

@requires_auth
def remove(apikey, body):
    return simple_return

@requires_auth
def add(apikey, body): 
    for entity in body:
        addRow('entities', entity)
    return simple_return

@requires_auth
def modify(apikey, body):
    return simple_return

def read(apikey, ids=None, category=None, name=None, description=None, count=None, page=None):
    return simple_return