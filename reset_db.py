import data
import contextlib

def main():
    with contextlib.suppress(Exception):
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
         {'name': 'lacking'},
         {'name': 'admin',
          'category': 'user',
          'description': 'the admin account'}
    ])
    with data.connection() as c:
        c.execute('INSERT INTO users VALUES("admin@yu-shan.com", ?, 123)', [entities[3]])

    relationships = data.addRows('relationships',
    [
        {'owner': entities[1],
         'property': entities[0],
         'user': entities[3]},
        {'owner': entities[3],
         'property': entities[1],
         'user': entities[3]}
    ])

if __name__ == '__main__':
    import plac; plac.call(main)