import mysql.connector

from config import *


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
    # TODO not sure how the correct data is saved?
    # as we only need to annotate auto alligned data e.g. is this already manually aligned data or not
    # maybe only select newest versions
    def get_audio(self):
        cur = self.dataBase.cursor()
        cur.execute("SELECT * FROM transcribed_audio_utterance ")
        rv = cur.fetchall()
        payload = []
        for result in rv:
            content = {'id': result['id'], 'audioStart': result['audioStart'], 'audioEnd': result['audioEnd'],
                       'text': result['text'], 'fileId': result['fileId'], 'speaker': result['speaker'],
                       'labeled': result['labeled'], 'correct': result['correct'], 'wrong': result['wrong']}
            payload.append(content)
        return None
