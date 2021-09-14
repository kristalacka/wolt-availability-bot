import sqlite3

class Database(object):
    def __init__(self):
        self._db_connection = sqlite3.connect('wolt.db')
        self._db_cur = self._db_connection.cursor()

    def query(self, query):
        ret = self._db_cur.execute(query)
        self._db_connection.commit()
        return ret

    def __del__(self):
        self._db_connection.close()