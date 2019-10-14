import mysql.connector as mariadb
import os
from xml.dom import minidom
from audio import AudioSnippet
from speaker import Speaker
from textSnippet import TextSnippet

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
    # AudioSnippet
    audioItemList = xmldoc.getElementsByTagName('tli')
    for s in audioItemList:
        audioSnippet = AudioSnippet
        audioSnippet.timelineId = s.attributes['id'].value
        audioSnippet.time = s.attributes['time'].value
        query = "INSERT INTO audioSnippets (timelineId, time, fileId) VALUES (%s, %s, %s)"
        cursor.execute(query, (
            audioSnippet.timelineId,
            audioSnippet.time,
            folderNumber
        ))
        dataBase.commit()
    # Speaker
    speakerItemList = xmldoc.getElementsByTagName('speaker')
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
        query = "INSERT INTO speaker (speakerId, sex, languageUsed, dialect, fileId) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(query, (
            speaker.speakerId,
            speaker.sex,
            speaker.languageUsed,
            speaker.dialect,
            folderNumber
        ))
        dataBase.commit()
    # TextSnippet
    textItemList = xmldoc.getElementsByTagName('tier')
    for textItem in textItemList:
        textSnippet = TextSnippet
        if textItem.hasAttribute('speaker'):
            textSnippet.speakerId = textItem.attributes['id'].value
            for event in textItem.getElementsByTagName('event'):
                textSnippet.start = event.attributes['start'].value
                textSnippet.end = event.attributes['end'].value
                textSnippet.text = event.firstChild.nodeValue
                cursor.execute(
                    "INSERT INTO textSnippets (speakerId, start, end, text, fileId) VALUES (%s, %s, %s, %s, %s)", (
                        textSnippet.speakerId,
                        textSnippet.start,
                        textSnippet.end,
                        textSnippet.text,
                        folderNumber
                    ))
                dataBase.commit()


if __name__ == "__main__":
    searchDirectories()
