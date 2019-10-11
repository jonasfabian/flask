import mysql.connector as mariadb
import os
from xml.dom import minidom

dataBase = mariadb.connect(
    host='localhost',
    user='root',
    passwd='password',
    database='labeling-tool'
)
cursor = dataBase.cursor()


def searchDirectories():
    print('Loading...')
    entries = os.scandir('C:\\Users\\Jonas\\Documents\\data')
    for entry in entries:
        for fileData in os.listdir('C:\\Users\\Jonas\\Documents\\data\\' + entry.name):
            if fileData.endswith(".xml"):
                extractDataToDB(entry.name)
    print('Done!')


def extractDataToDB(folderNumber: str):
    file = open('C:\\Users\\Jonas\\Documents\\data\\' + folderNumber + '\\indexes.xml')
    xmldoc = minidom.parse(file)
    audioItemList = xmldoc.getElementsByTagName('tli')
    for s in audioItemList:
        query = "INSERT INTO audioSnippets (timelineId, time) VALUES (%s, %s)"
        values = (s.attributes['id'].value, s.attributes['time'].value)
        cursor.execute(query, values)
        dataBase.commit()
    speakerItemList = xmldoc.getElementsByTagName('speaker')
    for speaker in speakerItemList:
        speakerId = speaker.attributes['id'].value
        sex = speaker.getElementsByTagName('sex')[0].attributes['value'].value
        lang = speaker.getElementsByTagName('language')[0].attributes['lang'].value
        dialect = 'CH'
        dialectElement = speaker.getElementsByTagName('ud-speaker-information')[0].getElementsByTagName(
            'ud-information')
        if len(dialectElement) > 0:
            dialect = dialectElement[0].firstChild.nodeValue
        query = "INSERT INTO speaker (speakerId, sex, languageUsed, dialect) VALUES (%s, %s, %s, %s)"
        values = (speakerId, sex, lang, dialect)
        cursor.execute(query, values)
        dataBase.commit()
    textItemList = xmldoc.getElementsByTagName('tier')
    for textItem in textItemList:
        speaker = 'unknown'
        if textItem.hasAttribute('speaker'):
            speaker = textItem.attributes['id'].value
            for event in textItem.getElementsByTagName('event'):
                cursor.execute("INSERT INTO textSnippets (speakerId, start, end, text) VALUES (%s, %s, %s, %s)", (
                speaker, event.attributes['start'].value, event.attributes['end'].value, event.firstChild.nodeValue))
                dataBase.commit()


if __name__ == "__main__":
    searchDirectories()
