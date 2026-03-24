import sqlite3

connection = sqlite3.connect("database/game.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    score INTEGER NOT NULL,
    level INTEGER NOT NULL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

connection.commit()
connection.close()

print("Database created successfully")