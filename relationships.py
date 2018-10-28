from auth import requires_auth
simple_return = {"resp": 0, "data": [], "error": ""}

@requires_auth
def remove(apikey, body):
    return simple_return

@requires_auth
def add(apikey, body): 
    return simple_return

@requires_auth
def modify(apikey, body):
    return simple_return

def read(apikey, ids=None, description=None, owner=None, _property=None, count=None, page=None):
    return simple_return