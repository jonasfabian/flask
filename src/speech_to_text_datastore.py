import mysql.connector

from src.config import *


class SpeechToTextDatastore:
    def __init__(self):
        self.dataBase = mysql.connector.connect(
            host='localhost',
            user=db_2_user,
            passwd=db_2_pw,
            database=database_2
        )
        # dataBase.cursor().execute("")
# TODO implement logic here
