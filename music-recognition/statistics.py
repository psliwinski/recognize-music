from libs.database import SqliteDb


def show_collisions():
    every = db.execute_all("""
        select count(hash) FROM descriptors      
    """)
    rows = db.execute_all("""
        select count(DISTINCT hash) FROM descriptors      
    """)
    val = 0
    if rows and every:
        if rows[0][0] and every[0][0] is not None:
            every = int(every[0][0])
            rows = int(rows[0][0])
            val = every - rows
        print('\n * kolizje: %d haszów' % val)


def show_duplicates():
    rows = db.execute_all("""
    SELECT a.song_dk, s.name, SUM(a.cnt)
    FROM (
      SELECT song_dk, COUNT(*) cnt
      FROM descriptors
      GROUP BY hash, song_dk, offset
      HAVING cnt > 1
      ORDER BY cnt ASC
    ) AS a
    JOIN songs s ON s.id = a.song_dk
    GROUP BY a.song_dk
  """) or []
    print(('\n * duplikaty: %s' % '%d utworów') % len(rows))
    for row in rows:
        print(('   ** %s %s: %s' % ('id=%s', '%s', '%d duplikaty')) % row)


def show_songs():
    rows = db.execute_all("""
    SELECT
      s.id,
      s.name,
      (SELECT COUNT(f.id) FROM descriptors AS f WHERE f.song_dk = s.id) AS descriptors_count
    FROM songs AS s
    ORDER BY descriptors_count DESC
  """) or []
    for row in rows:
        print(('   ** %s %s: %s' % ('id=%s', '%s', '%d haszów')) % row)


def show_summary():
    row = db.execute_one("""
    SELECT
      (SELECT COUNT(*) FROM songs) AS songs_count,
      (SELECT COUNT(*) FROM descriptors) AS descriptors_count
  """)
    if row:
        print(('\n * %s: %s (%s)' % ('razem', '%d utworów', '%d deskryptorów')) % row)
        return row[0]


if __name__ == '__main__':
    db = SqliteDb()
    show_summary()
    show_songs()
    show_duplicates()
    show_collisions()
