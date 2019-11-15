import mysql.connector

from config import user, passwd, database

dataBase = mysql.connector.connect(
    host='localhost',
    user=user,
    passwd=passwd,
    database=database
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
    dataBase = mysql.connector.connect(
        host='localhost',
        user=user,
        passwd=passwd,
        database=database
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
        PRIMARY KEY (id)) ENGINE = INNODB DEFAULT CHARSET = UTF8MB4""")

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
        UNIQUE KEY email (email)) ENGINE = INNODB DEFAULT CHARSET = UTF8MB4""")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS avatar (
        id BIGINT NOT NULL AUTO_INCREMENT,
        userId INT,
        avatar MEDIUMBLOB,
        PRIMARY KEY (id),
        UNIQUE KEY userId (userId)) ENGINE = INNODB DEFAULT CHARSET = UTF8MB4""")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS userAndTextAudio (
        id BIGINT NOT NULL AUTO_INCREMENT,
        userId INT,
        textAudioId INT,
        time TIMESTAMP,
        PRIMARY KEY (id),
        CONSTRAINT uni UNIQUE (userId, textAudioId)) ENGINE = INNODB DEFAULT CHARSET = UTF8MB4""")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS recordings (
        id BIGINT NOT NULL AUTO_INCREMENT,
        text MEDIUMTEXT CHARACTER SET utf8,
        userId INT NOT NULL,
        audio Mediumblob,
        PRIMARY KEY (id)) ENGINE = INNODB DEFAULT CHARSET = UTF8MB4""")

    cursor.execute(
        """CREATE TABLE IF NOT EXISTS textAudio (
        id BIGINT NOT NULL AUTO_INCREMENT,
        audioStart FLOAT NOT NULL,
        audioEnd FLOAT NOT NULL,
        text MEDIUMTEXT CHARACTER SET utf8,
        fileId Int NoT NULL,
        speaker VARCHAR(45),
        labeled INT,
        correct BIGINT,
        wrong BIGINT,
        PRIMARY KEY (id)) ENGINE = INNODB DEFAULT CHARSET = UTF8MB4""")


if __name__ == "__main__":
    dropDatabase()
    createDatabase()
    createTables()
