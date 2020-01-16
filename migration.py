import os
from xml.dom import minidom

import mysql.connector as mariadb

from config import baseDir, database, passwd, user

dataBase = mariadb.connect(
    host='localhost',
    user=user,
    passwd=passwd,
    database=database
)
cursor = dataBase.cursor()


def search_directories():
    print('Loading...')
    entries = os.scandir(baseDir)
    for entry in entries:
        for fileData in os.listdir(os.path.join(baseDir, entry.name)):
            if fileData.endswith(".xml"):
                extract_data_to_db(entry.name)
    print('Done!')


def extract_data_to_db(folderNumber: str):
    with open(os.path.join(baseDir, folderNumber, 'indexes.xml'), encoding='utf-8') as file:
        xml_doc = minidom.parse(file)
        audio_item_list = xml_doc.getElementsByTagName('tli')
        audio_time = {}
        for s in audio_item_list:
            audio_time.update({s.attributes['id'].value: s.attributes['time'].value})
        text_item_list = xml_doc.getElementsByTagName('tier')
        for textItem in text_item_list:
            if textItem.hasAttribute('speaker'):
                for event in textItem.getElementsByTagName('event'):
                    cursor.execute(
                        "INSERT INTO textAudio (audioStart, audioEnd, text, fileId, speaker, labeled, correct, wrong) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                        (audio_time.get(event.attributes['start'].value), audio_time.get(event.attributes['end'].value),
                         event.firstChild.nodeValue, folderNumber, textItem.attributes['speaker'].value, 0, 0, 0))
        speakerItemList = xml_doc.getElementsByTagName('speaker')
        for sp in speakerItemList:
            speakerId = sp.attributes['id'].value
            sex = sp.getElementsByTagName('sex')[0].attributes['value'].value
            languageUsed = sp.getElementsByTagName('language')[0].attributes['lang'].value
            dialect = '-'
            dialectElement = sp.getElementsByTagName('ud-speaker-information')[0].getElementsByTagName(
                'ud-information')
            if len(dialectElement) > 0:
                dialect = dialectElement[0].firstChild.nodeValue
            cursor.execute("INSERT INTO speaker (speakerId, sex, languageUsed, dialect) VALUES (%s, %s, %s, %s)",
                           (speakerId, sex, languageUsed, dialect))
            dataBase.commit()


if __name__ == "__main__":
    search_directories()
