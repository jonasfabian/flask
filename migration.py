import mysql.connector as mariadb
import os
from xml.dom import minidom
from speaker import Speaker

dataBase = mariadb.connect(
    host='localhost',
    user='root',
    passwd='password',
    database='labeling-tool'
)
cursor = dataBase.cursor()


def searchDirectories():
    print('Loading...')
    entries = os.scandir("C:\\Users\\Jonas\\Documents\\data\\")
    for entry in entries:
        for fileData in os.listdir("C:\\Users\\Jonas\\Documents\\data\\" + entry.name + "\\"):
            if fileData.endswith(".xml"):
                extractDataToDB(entry.name)
    print('Done!')


def extractDataToDB(folderNumber: str):
    file = open('C:\\Users\\Jonas\\Documents\\data\\' + folderNumber + '\\indexes.xml')
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
                    (
                        audio_time.get(event.attributes['start'].value),
                        audio_time.get(event.attributes['end'].value),
                        event.firstChild.nodeValue,
                        folderNumber,
                        textItem.attributes['speaker'].value,
                        0, 0, 0
                    ))
    speakerItemList = xml_doc.getElementsByTagName('speaker')
    for sp in speakerItemList:
        speaker = Speaker
        speaker.speakerId = sp.attributes['id'].value
        speaker.sex = sp.getElementsByTagName('sex')[0].attributes['value'].value
        speaker.languageUsed = sp.getElementsByTagName('language')[0].attributes['lang'].value
        speaker.dialect = '-'
        dialectElement = sp.getElementsByTagName('ud-speaker-information')[0].getElementsByTagName(
            'ud-information')
        if len(dialectElement) > 0:
            speaker.dialect = dialectElement[0].firstChild.nodeValue
        query = "INSERT INTO speaker (speakerId, sex, languageUsed, dialect) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (
            speaker.speakerId,
            speaker.sex,
            speaker.languageUsed,
            speaker.dialect
        ))
        dataBase.commit()


if __name__ == "__main__":
    searchDirectories()
