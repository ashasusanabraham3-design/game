import sqlite3

conn = sqlite3.connect("database/game.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM scores")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()