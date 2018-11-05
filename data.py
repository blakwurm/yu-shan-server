import sqlite3
from yaml import load
import json
from contextlib import contextmanager, suppress
from itertools import zip_longest
import random
from baseconv import base62
import os
from functools import partial

__db_constants__ = {}
with open('database_info.yml') as infofile:
    __db_constants__ = load(infofile)

# print(__db_constants__)

@contextmanager
def connection():
    conn = sqlite3.connect(__db_constants__['dbname'])
    c = conn.cursor()
    try:
        yield c
    except Exception as e:
        print('There was an exception while connected to the database')
        conn.close()
        raise e
    conn.commit()
    conn.close()

def connector(func):
    def callConnect(*args, **kwds):
        with connection() as c:
            kwds.update({'c': c})
            return func(*args, **kwds)
    return callConnect

def create_db():
    os.remove(__db_constants__['dbname'])
    with connection() as c:
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
def addRows(table_name, things_to_insert, *, genNewID = True, c):
    results = []
    idfield = keycolumn_for(table_name)
    for thing in things_to_insert:
        tableinfo = __db_constants__['tables'][table_name]
        new_id = genCheckedID(table_name, keycolumn_for(table_name))
        cols = list(map(lambda a: a['name'], tableinfo['columns']))
        insertion = pack_data(table_name, thing)
        if genNewID:
            insertion.update({idfield: new_id}) 
        strcols = ', '.join(cols)
        strplc = ':'+', :'.join(cols)
        print('insertion is {ins}'.format(ins=insertion))
        rrr = c.execute(
            "INSERT INTO {tn} VALUES ({strplc})".format(
                tn = table_name,
                strcols = strcols,
                strplc = strplc
            ),
                     insertion
        )
        results.append(new_id)
    print("results are {a}".format(a = results))
    return results


def only_key(keyname, default):
    def retfn(a):
        return a.get(keyname, default)
    return retfn

def cols_for_table_name(table_name):
    return list(map(only_key('name', None) ,__db_constants__['tables'][table_name]['columns']))

def pack_data(table_name, thing_to_pack):
    packed = {}
    print('we packin {a}'.format(a=thing_to_pack))
    if thing_to_pack:
        print('thing is ' + str(thing_to_pack))
        cols = cols_for_table_name(table_name)
        thing_copy = {**thing_to_pack}
        for key in cols:
            value = None
            if key == 'extra':
                value = json.dumps(thing_copy)
            else:
                value = thing_copy.pop(key, None)
            packed.update({key: value})
        print('packed is {p}, while original is {t}'.format(p=packed, t=thing_to_pack))
    return None if packed is {} else packed

@connector
def readRows(table_name, queries, c):
    tableinfo = __db_constants__['tables'][table_name]
    cols = list(map(lambda a: a['name'], tableinfo['columns']))
    page = queries.pop('page', 1)
    count = queries.pop('count', 10)
    method = queries.pop('method', 'and')
    safe_query_keys = []
    for key in cols:
        if queries.get(key, None):
            safe_query_keys.append(key)
    print('queries are {a}'.format(a=queries))
    querymethod = ' AND ' if method is 'and' else ' OR '
    queryplug = querymethod.join(list(map(lambda a: '{a} = :{a}'.format(a = a), safe_query_keys)))
    querystring = "SELECT * FROM {tn} {where} {qp} LIMIT {limit} OFFSET {offset}".format(
        tn = table_name,
        qp = queryplug,
        where = 'WHERE' if queryplug else '',
        limit = count,
        offset = (page - 1) * count
    )
    print('querystring is ' + querystring)
    c.execute(querystring, queries)
    all_rows = c.fetchall()
    ret_rows = []
    for row in all_rows:
        packed_data = dict(zip_longest(cols, row))
        extra = packed_data.pop('extra', None)
        if extra:
            packed_data.update(json.loads(extra))
        cleaned_row = {k: v for k, v in packed_data.items() if v is not None}
        ret_rows.append(cleaned_row)
    return ret_rows

def first(a_list):
    return next(iter(a_list), None)

def read_multiple_ids(table_name, idlist):
    idcolumn = keycolumn_for(table_name)
    return list(map(lambda a: first(readRows(table_name, {idcolumn: a})), idlist))

@connector
def modifyRows(table_name, modifications, c):
    idcolumn = keycolumn_for(table_name)
    idlist = list(map(lambda a: a.get(idcolumn, None) if a else '', modifications))
    existant = read_multiple_ids(table_name, idlist)
    combo = []
    packed = []
    results = []
    for old, new in zip_longest(existant, modifications):
        if old and new:
            combo.append({**old, **new})
        else:
            combo.append(None)
    packed = list(map(partial(pack_data, table_name), combo))
    placeholders = _make_update_placeholder(table_name)
    querystring = 'UPDATE {tn} SET {plc} WHERE {idc} = :{idc}'.format(
        tn = table_name, idc = idcolumn, plc = placeholders)
    print('packed is {a}'.format(a=packed))
    for change in packed:
        if change:
            c.execute(querystring, change)
            results.append(change['id'])
        else:
            print('doin else with {a}'.format(a=change))
            print('results is {a}'.format(a=results))
            results.append(None)
    return results

def _make_update_placeholder(table_name):
    column_names = list(map(lambda a: a['name'], __db_constants__['tables'][table_name]['columns']))
    placeholders = list(map(lambda a: '{a} = :{a}'.format(a=a), column_names))
    return ', '.join(placeholders)

def keycolumn_for(table_name):
    return __db_constants__['tables'][table_name]['columns'][0]['name']
        
@connector
def deleteRow(table_name, entity_to_delete, c):
    cols = cols_for_table_name(table_name)
    keycol = keycolumn_for(table_name)
    read_results = readRows(table_name, entity_to_delete)
    original_entity = read_results[0] if read_results else {}
    actually_delete = original_entity == entity_to_delete
    print('we should delete {a}'.format(a=entity_to_delete))
    print('it will delete {a}'.format(a=original_entity))
    if actually_delete:
        c.execute('DELETE FROM {tn} WHERE {kc} = :{kc}'.format(tn=table_name, kc=keycol),
                  original_entity) 
        return original_entity[keycol]
    else:
        return None
   
@connector
def genCheckedID(table_name, idfield, c):
    ret_id = None
    while not ret_id:
        ten_id = genID(table_name)
        query = 'SELECT * FROM {tn} WHERE {idname} = ?'.format(
            tn = table_name,
            idname = idfield
        )
        c.execute(query, [ten_id])
        existant_thing = c.fetchone()
        if not existant_thing:
            ret_id = ten_id
    return ret_id

def genID(table_name):
    return 'YU{a}3{b}'.format(a = table_name[slice(0, 3)], b = random64())

def random64():
    return base62.encode(random.randint(9, 999999999999999999999999))

def buildResponse(datalist, *, errors = {}):
    real_list = datalist if isinstance(datalist, list) else [datalist]
    def getErrorCode(thingy):
        try:
            return errors[thingy]
        except:
            return (0, '')
    codes = [getErrorCode(x) for x in real_list]
    error_results = [x for x in codes if x[0]]
    errorcode, errormessage = error_results[0] if error_results else (0, '')
    print(error_results)
    return {'resp': errorcode, 'error': errormessage, 'data': real_list}

non_imp_response = {'resp': -1, 'error': 'Functionality not Implimented', 'data': []}