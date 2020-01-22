import mysql.connector

from src.config import db_1_user, db_1_pw, database_1

if __name__ == "__main__":
    script = open("./src/setup_db.sql", "r+").read()
    dataBase = mysql.connector.connect(
        host='localhost',
        user=db_1_user,
        passwd=db_1_pw,
        database=database_1
    )
    dataBase.cursor().execute(script)
    print("created database")
