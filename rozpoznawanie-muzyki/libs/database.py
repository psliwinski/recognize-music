from itertools import zip_longest
import sqlite3


class SqliteDb:
    descriptors_table = 'descriptors'
    songs_table = 'songs'

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        self.connection = sqlite3.connect('db/descriptors.db')
        self.cursor = self.connection.cursor()

    def count_song_hashes(self, song_id):
        select_query = 'SELECT COUNT(*) FROM %s WHERE song_dk = %d' % (self.descriptors_table, song_id)
        rows = self.execute_one(select_query)
        return rows[0]

    def insert_many(self, table, columns, descriptors_set):
        def hash_grouper(iterable, n):
            args = [iter(iterable)] * n
            return (filter(None, valuesx) for valuesx
                    in zip_longest(fillvalue=None, *args))
        for split_hashes in hash_grouper(descriptors_set, 1000):
            insert_query = "INSERT OR IGNORE INTO %s (%s) VALUES (?, ?, ?)" % (table, ", ".join(columns))
            self.cursor.executemany(insert_query, split_hashes)
            self.connection.commit()

    def insert_one(self, params):
        keys = ', '.join(params.keys())
        values_list = list(params.values())
        insert_query = "INSERT INTO songs (%s) VALUES (?, ?)" % keys
        self.cursor.execute(insert_query, values_list)
        self.connection.commit()
        return self.cursor.lastrowid

    def find_one(self, table, value):
        select = self.create_select(table, value)
        return self.execute_one(select['query'], select['descriptors_set'])

    @staticmethod
    def create_select(table, params):
        conditions = []
        values = []
        for i, k in enumerate(params):
            key = k
            value = params[k]
            conditions.append("%s = ?" % key)
            values.append(value)
        conditions = ' AND '.join(conditions)
        select_query = "SELECT * FROM %s WHERE %s" % (table, conditions)
        return {
            "query": select_query,
            "descriptors_set": values
        }

    def execute_all(self, query, values=()):
        self.cursor.execute(query, values)
        return self.cursor.fetchall()

    def execute_one(self, query, values=()):
        self.cursor.execute(query, values)
        return self.cursor.fetchone()

    def query(self, query, values=()):
        self.cursor.execute(query, values)

    def save_descriptors(self, descriptors_set):
        self.insert_many(self.descriptors_table,
                         ['song_dk', 'hash', 'offset'], descriptors_set)

    def find_song_by_id(self, idx):
        return self.find_one(self.songs_table, {"id": idx})

    def save_song(self, file_name, file_hash):
        song_row = self.find_song_by_file_hash(file_hash)
        if song_row:
            song_id = song_row[0]
        else:
            song_id = self.insert_one({"name": file_name, "file_hash": file_hash})  #
        return song_id

    def find_song_by_file_hash(self, file_hash):
        return self.find_one(self.songs_table, {"file_hash": file_hash})

    def __del__(self):
        self.connection.commit()
        self.connection.close()
