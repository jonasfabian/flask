import mysql.connector as mariadb

dataBase = mariadb.connect(
    host='localhost',
    user='root',
    passwd='password'
)
cursor = dataBase.cursor()


def dropDatabase():
    cursor.execute("DROP DATABASE IF EXISTS `labeling-tool`")
    print("Dropped database")


def createDatabase():
    global dataBase
    global cursor
    cursor.execute("CREATE DATABASE IF NOT EXISTS `labeling-tool`")
    dataBase.close()
    dataBase = mariadb.connect(
        host='localhost',
        user='root',
        passwd='password',
        database='labeling-tool'
    )
    cursor = dataBase.cursor()


def createTables():
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS audioSnippets (
        id BIGINT NOT NULL AUTO_INCREMENT,
        timelineId VARCHAR(45),
        time FLOAT NOT NULL,
        PRIMARY KEY (id))""")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS speaker (
        id BIGINT NOT NULL AUTO_INCREMENT,
        speakerId VARCHAR(45),
        sex VARCHAR(45),
        languageUsed VARCHAR(45),
        dialect VARCHAR(45),
        PRIMARY KEY (id))""")

def main():
    dropDatabase()
    createDatabase()
    createTables()


if __name__ == "__main__":
    main()
