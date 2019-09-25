import mysql.connector

dataBase = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='password',
    database='labeling-tool'
)
cursor = dataBase.cursor()

def dropTables():
    cursor.execute("DROP TABLE IF EXISTS audio")
    cursor.execute("DROP TABLE IF EXISTS avatar")
    cursor.execute("DROP TABLE IF EXISTS flyway_schema_history")
    cursor.execute("DROP TABLE IF EXISTS textAudioIndex")
    cursor.execute("DROP TABLE IF EXISTS transcript")
    cursor.execute("DROP TABLE IF EXISTS chat")
    cursor.execute("DROP TABLE IF EXISTS chatMember")
    cursor.execute("DROP TABLE IF EXISTS chatMessage")
    cursor.execute("DROP TABLE IF EXISTS user")
    cursor.execute("DROP TABLE IF EXISTS userAndTextAudioIndex")
    print("Dropped all tables")

def main():
    dropTables()



if __name__ == "__main__":
    main()
