import sqlite3
from yaml import load
import json


__db_constants__ = {}
with open('database_info.yml') as infofile:
    __db_constants__ = load(infofile)

# print(__db_constants__)

conn = sqlite3.connect(__db_constants__['dbname'])
c = conn.cursor()

def create_db():
    for key, table in __db_constants__['tables'].items():
        keyrow = table['columns'][0]
        c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'\
            .format(tn=table['name'], nf=keyrow['name'], ft=keyrow['type']))
        for columndata in table['columns'][1:]:
            c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ct}"\
                .format(tn=table['name'], cn=columndata['name'], ct=columndata['type']))
    conn.commit()

def addRow(table_name, thing_to_insert):
    tableinfo = __db_constants__['tables'][table_name]
    thing_copy = {**thing_to_insert}
    cols = list(map(lambda a: a['name'], tableinfo['columns']))
    insertion = {}
    for key in cols:
        insertion.update({key: thing_copy.pop(key, None)\
                                    if key != 'extra' else\
                               json.dumps(thing_copy)})

    strcols = ', '.join(cols)
    strplc = ':'+', :'.join(cols)
    print(strcols)
    print(strplc)
    c.execute("INSERT OR IGNORE INTO {tn} VALUES ({strplc})"\
                .format(tn = table_name, strcols = strcols, strplc = strplc),
                 insertion)
    conn.commit()
    pass