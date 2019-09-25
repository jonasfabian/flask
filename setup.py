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
    # Table audio
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS audio (
        id BIGINT NOT NULL AUTO_INCREMENT,
        path VARCHAR(200),
        fileId BIGINT NOT NULL,
        PRIMARY KEY (id))""")

    # Table audio
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS textAudioIndex (
        id BIGINT NOT NULL AUTO_INCREMENT,
        samplingRate INT,
        textStartPos INT,
        textEndPos INT,
        audioStartPos INT,
        audioEndPos INT,
        speakerKey INT,
        labeled INT default 0,
        correct INT default 0,
        wrong INT default 0,
        transcript_file_id INT,
        PRIMARY KEY (id))""")

    # Table transcript
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS transcript (
        id BIGINT NOT NULL AUTO_INCREMENT,
        text MEDIUMTEXT CHARACTER SET utf8,
        fileId BIGINT NOT NULL,
        PRIMARY KEY (id))""")

    # Table user
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS user (
        id BIGINT NOT NULL AUTO_INCREMENT,
        firstName VARCHAR (100),
        lastName VARCHAR (100),
        email VARCHAR (100),
        username VARCHAR(100),
        avatarVersion INT,
        password VARCHAR (100),
        PRIMARY KEY (id),
        UNIQUE KEY email (email))""")

    # Table userAndTextAudioIndex
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS userAndTextAudioIndex (
        id BIGINT NOT NULL AUTO_INCREMENT,
        userId INT,
        textAudioIndexId INT,
        time TIMESTAMP,
        PRIMARY KEY (id),
        CONSTRAINT uni UNIQUE (userId, textAudioIndexId))""")

    # Table avatar
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS avatar (
        id BIGINT NOT NULL AUTO_INCREMENT,
        userId INT,
        avatar BLOB,
        PRIMARY KEY (id),
        UNIQUE KEY userId (userId))""")


def main():
    dropDatabase()
    createDatabase()
    createTables()


if __name__ == "__main__":
    main()
