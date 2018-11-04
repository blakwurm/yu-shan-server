import data
import auth
import contextlib
import time

def main(adminpass):
    with data.connection() as c:
        data.create_db()
    entities = data.addRows('entities',
    [ 
        {'name': 'simple', 
         'description': 'simple entry',
         'category':'rulebook'},
        {'name': 'A bit extra',
         'description': 'a complex entry',
         'category': 'character',
         'subcategory': 'simple',
         'variation': 'USB'},
         {'name': 'lacking'}
    ])

    adminID = auth.makeNewUser(email = 'admin@yu-shan.com', newpass = adminpass)

    relationships = data.addRows('relationships',
    [
        {'owner': entities[1],
         'property': entities[0],
         'user': adminID},
        {'owner': adminID,
         'property': entities[1],
         'user': adminID}
    ])

if __name__ == '__main__':
    import plac; plac.call(main)