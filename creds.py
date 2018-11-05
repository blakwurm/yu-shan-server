from yaml import load

def getCredsFor(servicename):
    with open('creds.yml') as credfile:
        cred = load(credfile).get(servicename, {'username': '', 'password': ''})
        return (cred['username'], cred['password'])