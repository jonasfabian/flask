import mysql.connector

from src.config import user, passwd, database

if __name__ == "__main__":
    script = open("./src/setup_db.sql", "r+").read()
    dataBase = mysql.connector.connect(
        host='localhost',
        user=user,
        passwd=passwd,
        database=database
    )
    dataBase.cursor().execute(script)
    print("created database")
