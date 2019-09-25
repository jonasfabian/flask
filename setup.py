import mysql.connector

dataBase = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='password',
    database='labeling-tool'
)
cursor = dataBase.cursor()


def dropTables():
    cursor.execute("DROP DATABASE `labeling-tool`")
    print("Dropped database")


def main():
    dropTables()


if __name__ == "__main__":
    main()
