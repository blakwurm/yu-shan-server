import sqlite3
from yaml import load
import json
from contextlib import contextmanager


__db_constants__ = {}
with open('database_info.yml') as infofile:
    __db_constants__ = load(infofile)

# print(__db_constants__)

@contextmanager
def connection():
    conn = sqlite3.connect(__db_constants__['dbname'])
    c = conn.cursor()
    yield c
    conn.commit()
    conn.close()

def connector(func):
    def callConnect(*args, **kwds):
        with connection() as c:
            kwds.update({'c': c})
            func(*args, **kwds)
    return callConnect

@connector
def create_db(c):
    for key, table in __db_constants__['tables'].items():
        keyrow = table['columns'][0]
        c.execute(
            'CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'.format(
                tn=table['name'],
                nf=keyrow['name'],
                ft=keyrow['type']
            )
        )
        for columndata in table['columns'][1:]:
            c.execute(
                "ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}".format(
                    tn=table['name'],
                    cn=columndata['name'], 
                    ct=columndata['type']
                )
            )

@connector
def addRow(table_name, thing_to_insert, c):
    tableinfo = __db_constants__['tables'][table_name]
    thing_copy = {**thing_to_insert}
    cols = list(map(lambda a: a['name'], tableinfo['columns']))
    insertion = {}
    for key in cols:
        insertion.update(
            {key: thing_copy.pop(key, None)
                    if key != 'extra'
                    else json.dumps(thing_copy)}
        )
    strcols = ', '.join(cols)
    strplc = ':'+', :'.join(cols)
    c.execute(
        "INSERT OR IGNORE INTO {tn} VALUES ({strplc})".format(
            tn = table_name,
            strcols = strcols,
            strplc = strplc
        ),
                 insertion
    )

@connector
def readRow(table_name, queries, c):
    tableinfo = __db_constants__['tables'][table_name]
    cols = list(map(lambda a: a['name'], tableinfo['columns']))
    page = queries.pop('page', 1)
    count = queries.pop('count', 10)
    safe_query_keys = []
    for key in cols:
        if queries.get(key, None):
            safe_query_keys.append(key)
    queryplug = ' AND '.join(list(map(lambda a: '{a} = :{a}'.format(a = a), safe_query_keys)))
    querystring = "SELECT * FROM {tn} WHERE {qp} LIMIT {limit} OFFSET {offset}".format(
        tn = table_name,
        qp = queryplug,
        limit = count,
        offset = (page - 1) * count
    )
    c.execute(querystring, queries)
    all_rows = c.fetchall()
    print(all_rows)
    pass