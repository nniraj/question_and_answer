import sqlite3

with open('schema.sql', 'r') as sql_file:
    sql_script = sql_file.read()

query = "update users set expert=1 where id=4"
db = sqlite3.connect('questions.db')
cursor = db.cursor()
cursor.executescript(query)
db.commit()
db.close()