import mysql.connector
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager
from flask_restful import Api
from flask_bcrypt import Bcrypt

import user

app = Flask(__name__)
api = Api(app)
app.secret_key = b'myzFrIhsQHIGDWSIHbtIL6QPTGAqvxS5'

loginManager = LoginManager()
loginManager.init_app(app)

bcrypt = Bcrypt(app)

CORS(app)
dataBase = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='password',
    database='labeling-tool'
)
cursor = dataBase.cursor()


@app.route("/checkLogin", methods=['POST'])
def checkLogin():
    userr = user
    return jsonify(
        {'Authenticated': userr.User.is_authenticated(app, bcrypt, request.json['email'], request.json['password'])})


# Create a user
@app.route("/createUser", methods=['POST'])
def createUser():
    pw = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
    cursor.execute(
        "INSERT INTO user(id, firstName, lastName, email, username, avatarVersion, password, canton) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
        (request.json['id'], request.json['firstName'], request.json['lastName'], request.json['email'],
         request.json['username'], request.json['avatarVersion'], pw, request.json['canton']))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get a user by Id
@app.route("/getUserById", methods=['GET'])
def getUserById():
    cursor.execute("SELECT * FROM user WHERE id = %s", (request.args.get('id'),))
    rv = cursor.fetchall()
    for result in rv:
        content = {'id': result[0], 'firstName': result[1], 'lastName': result[2], 'email': result[3],
                   'username': result[4], 'avatarVersion': result[5]}
    return jsonify(content)


# Get a user by username
@app.route("/getUserByUsername", methods=['GET'])
def getUserByUsername():
    cursor.execute("SELECT * FROM user WHERE username = %s", (request.args.get('username'),))
    rv = cursor.fetchall()
    for result in rv:
        content = {'id': result[0], 'firstName': result[1], 'lastName': result[2], 'email': result[3],
                   'username': result[4], 'avatarVersion': result[5]}
    return jsonify(content)


# Get a user by email
@app.route("/getUserByEmail", methods=['GET'])
def getUserByEmail():
    cursor.execute("SELECT * FROM user WHERE email = %s", (request.args.get('email'),))
    rv = cursor.fetchall()
    for result in rv:
        content = {'id': result[0], 'firstName': result[1], 'lastName': result[2], 'email': result[3],
                   'username': result[4], 'avatarVersion': result[5]}
    return jsonify(content)


# Get top five users by amount of labeled instances
@app.route("/getTopFiveUsersLabeledCount", methods=['GET'])
def getTopFiveUsersLabeledCount():
    cursor.execute(
        "SELECT user.id, user.username, COUNT(userAndTextAudioIndex.id) FROM userAndTextAudioIndex JOIN user ON user.id = userAndTextAudioIndex.userId GROUP BY user.id")
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {'userId': result[0], 'username': result[1], 'labelCount': result[2]}
        payload.append(content)
        content = {}
    return jsonify(payload)


# Update a user
@app.route("/updateUser", methods=['PUT'])
def updateUser():
    pw = bcrypt.generate_password_hash(request.json['password'])
    cursor.execute(
        "UPDATE user SET firstName = %s, lastName = %s, email = %s, username = %s, avatarVersion = %s, password = %s WHERE id = %s",
        (request.json['firstName'], request.json['lastName'], request.json['email'],
         request.json['username'], request.json['avatarVersion'], pw, request.json['id']))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Delete a user
@app.route("/deleteUser", methods=['DELETE'])
def deleteUser():
    cursor.execute("DELETE FROM user WHERE id = %s", (request.args.get('id'),))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getAudioSnippet", methods=['GET'])
def getAudioSnippet():
    cursor.execute("SELECT * FROM audiosnippets WHERE timelineId = %s", (request.args.get('timelineId'),))
    rv = cursor.fetchall()
    for result in rv:
        content = {'id': result[0], 'timelineId': result[1], 'time': result[2], 'fileId': result[3]}
    return jsonify(content)


@app.route("/getTextSnippet", methods=['GET'])
def getTextSnippet():
    cursor.execute("SELECT * FROM textsnippets WHERE id = %s", (request.args.get('id'),))
    rv = cursor.fetchall()
    for result in rv:
        content = {'id': result[0], 'speakerId': result[1], 'start': result[2], 'end': result[3], 'text': result[4], 'fileId': result[5]}
    return jsonify(content)


@app.route("/getSpeaker", methods=['GET'])
def getSpeaker():
    cursor.execute("SELECT * FROM speaker WHERE speakerId = %s", (request.args.get('speakerId'),))
    rv = cursor.fetchall()
    for result in rv:
        content = {'id': result[0], 'speakerId': result[1], 'sex': result[2], 'languageUsed': result[3],
                   'dialect': result[4], 'fileId': result[5]}
    return jsonify(content)


# Get ten not yet labeled textAudioIndexes
@app.route("/getTenNonLabeledDataIndexes", methods=['GET'])
def getTenNonLabeledDataIndexes():
    cursor.execute(
        "SELECT textAudioIndex.*, transcript.fileId, transcript.text FROM textAudioIndex JOIN transcript ON textAudioIndex.transcript_file_id = transcript.fileId WHERE textAudioIndex.labeled = 0 ORDER BY textAudioIndex.id ASC LIMIT 10")
    ids = cursor.fetchall()
    payload = []
    content = {}
    for vi in ids:
        content = {
            'id': vi[0], 'samplingRate': vi[1], 'textStartPos': vi[2], 'textEndPos': vi[3],
            'audioStartPos': vi[4], 'audioEndPos': vi[5], 'speakerKey': vi[6], 'labeled': vi[7],
            'correct': vi[8], 'wrong': vi[9], 'fileId': vi[10], 'text': vi[11]
        }
        payload.append(content)
    return jsonify(payload)


# Get textAudioIndex by labeled type
@app.route("/getTextAudioIndexesByLabeledType", methods=['GET'])
def getTextAudioIndexesByLabeledType():
    cursor.execute("SELECT * FROM textAudioIndex WHERE labeled = %s", (request.args.get('labeledType'),))
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {
            'id': result[0], 'samplingRate': result[1], 'textStartPos': result[2], 'textEndPos': result[3],
            'audioStartPos': result[4], 'audioEndPos': result[5], 'speakerKey': result[6], 'labeled': result[6],
            'correct': result[7], 'wrong': result[8], 'transcript_file_id': result[9]
        }
        payload.append(content)
        content = {}
    return jsonify(payload)


# Create a userAndTextAudioIndex
@app.route("/createUserAndTextAudioIndex", methods=['POST'])
def createUserAndTextAudioIndex():
    cursor.execute(
        "INSERT INTO userAndTextAudioIndex(userId, textAudioIndexId, time) VALUES(%s, %s, %s)",
        (request.json['userId'], request.json['textAudioIndexId'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get top five users by labeling amount
@app.route("/getTopFive", methods=['GET'])
def getTopFiveUsersByLabelCount():
    cursor.execute(
        "SELECT user.id, user.username, count(userAndTextAudioIndex.userId) FROM userAndTextAudioIndex JOIN user ON user.id = userAndTextAudioIndex.userId GROUP BY user.id LIMIT 5")
    rv = cursor.fetchall()
    print(rv)
    payload = []
    content = {}
    for result in rv:
        content = {
            'id': result[0], 'username': result[1], 'count': result[2]
        }
        payload.append(content)
        content = {}
    return jsonify(payload)


# Get sums of labeled
@app.route("/getLabeledSums", methods=['GET'])
def getLabeledSums():
    cursor.execute("SELECT COUNT(textAudioIndex.id) FROM textAudioIndex WHERE textAudioIndex.correct != 0")
    correct = cursor.fetchone()
    cursor.execute("SELECT COUNT(textAudioIndex.id) FROM textAudioIndex WHERE textAudioIndex.wrong != 0")
    wrong = cursor.fetchone()
    cursor.execute("SELECT COUNT(textAudioIndex.id) FROM textAudioIndex")
    totalTextAudioIndexes = cursor.fetchone()
    return jsonify({'correct': correct[0], 'wrong': wrong[0], 'total': totalTextAudioIndexes[0]})


# Get audio file
@app.route("/getAudioFile", methods=['GET'])
def getAudioFile():
    path = "C:\\Users\\Jonas\\Documents\\data\\" + request.args.get('fileId')
    return send_from_directory(path, 'audio.wav')


# Create avatar
@app.route("/createAvatar", methods=['GET'])
def createAvatar():
    cursor.execute("DELETE FROM avatar WHERE avatar.userId = %s", (request.json['userId'],))
    dataBase.commit()
    cursor.execute("INSERT INTO avatar(userId, avatar) VALUES(%s, %s)",
                   (request.json['userId'], request.json['avatar'],))
    dataBase.commit()

# Get avatar
@app.route("/getAvatar", methods=['GET'])
def getAvatar():
    cursor.execute("SELECT FROM avatar WHERE avatar.userId = %s", (request.args.get('userId'),))
    avatar = cursor.fetchall()
    return jsonify(avatar)


if __name__ == '__main__':
    app.run(port=8080)
