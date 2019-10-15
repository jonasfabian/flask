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
        """CREATE TABLE IF NOT EXISTS speaker (
        id BIGINT NOT NULL AUTO_INCREMENT,
        speakerId VARCHAR(45),
        sex VARCHAR(45),
        languageUsed VARCHAR(45),
        dialect VARCHAR(45),
        fileId Int NOT NULL,
        PRIMARY KEY (id))""")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS user (
        id BIGINT NOT NULL AUTO_INCREMENT,
        firstName VARCHAR (100),
        lastName VARCHAR (100),
        email VARCHAR (100),
        username VARCHAR(100),
        avatarVersion INT,
        password VARCHAR (100),
        canton VARCHAR(45),
        PRIMARY KEY (id),
        UNIQUE KEY email (email))""")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS avatar (
        id BIGINT NOT NULL AUTO_INCREMENT,
        userId INT,
        avatar BLOB,
        PRIMARY KEY (id),
        UNIQUE KEY userId (userId))""")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS userAndTextAudioIndex (
        id BIGINT NOT NULL AUTO_INCREMENT,
        userId INT,
        textAudioIndexId INT,
        time TIMESTAMP,
        PRIMARY KEY (id),
        CONSTRAINT uni UNIQUE (userId, textAudioIndexId))""")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS recordings (
        id BIGINT NOT NULL AUTO_INCREMENT,
        text MEDIUMTEXT CHARACTER SET utf8,
        userId INT NOT NULL,
        audio BLOB,
        PRIMARY KEY (id))""")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS textAudio (
        id BIGINT NOT NULL AUTO_INCREMENT,
        audioStart FLOAT NOT NULL,
        audioEnd FLOAT NOT NULL,
        text MEDIUMTEXT,
        fileId Int NoT NULL,
        PRIMARY KEY (id))""")


def main():
    dropDatabase()
    createDatabase()
    createTables()


if __name__ == "__main__":
    main()
