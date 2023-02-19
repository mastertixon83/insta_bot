from data.config import *
import psycopg2

from db_api.db_commands import DBCommands

db = DBCommands()

print(db.add_new_user())

conn_string = f"host={host} dbname={DB_NAME} user={PG_USER} password={PG_PASS}"
conn = psycopg2.connect(conn_string)

with open("db_api/create_db.sql", "r") as file:
    create_db_command = file.read()
with conn.cursor() as cursor:
    try:
        cursor.execute(create_db_command)
    except:
        print("I can't drop our test database!")

    conn.commit()  # <--- makes sure the change is shown in the database