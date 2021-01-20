#!/usr/bin/python
from libs.database import SqliteDb

if __name__ == '__main__':
    db = SqliteDb()
    db.query("DROP TABLE IF EXISTS descriptors;")

    print("Usunięto tabelę \'descriptors\'")
    db.query("""
    CREATE TABLE `descriptors` (
      `id`  INTEGER PRIMARY KEY AUTOINCREMENT,
      `song_dk` INTEGER,
      `hash`  TEXT,
      `offset`  INTEGER
    );
  """)
    print("Utworzono tabelę \'descriptors\'")
    db.query("DROP TABLE IF EXISTS songs;")

    print("Usunięto tabelę \'songs\'")
    db.query("""
       CREATE TABLE songs (
         id  INTEGER PRIMARY KEY AUTOINCREMENT,
         name  TEXT,
         file_hash  TEXT
       );
     """)
    print("Utworzono tabelę \'songs\'")
