#!/usr/bin/python
from configparser import ConfigParser
import psycopg2


# Получаем параметры из конфига для базы
def config(filename='database.ini', section='postgresql'):
    # create parser
    parser = ConfigParser()
    parser.read(filename)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
    return db


def get_cursor():
    """ Connect to the PostgreSQL """
    conn = None
    try:
        params = config()
        print("Connecting to the PostgreSQL database...")
        conn = psycopg2.connect(**params)

        cur = conn.cursor()
        return cur
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
'''
    finally:
        if conn is not None:
            conn.close()
            print('Database connection closed')
'''

if __name__ == "__main__":
    CURS = get_cursor()
    CURS.execute('Select uid from bot_all."Users"')
    print(CURS.fetchall())