import mysql.connector
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from flask_login import LoginManager
from flask_restful import Api
from flask_bcrypt import Bcrypt
import json

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
                   'username': result[4], 'avatarVersion': result[5], 'canton': result[7]}
    return jsonify(content)


# Get a user by username
@app.route("/getUserByUsername", methods=['GET'])
def getUserByUsername():
    cursor.execute("SELECT * FROM user WHERE username = %s", (request.args.get('username'),))
    rv = cursor.fetchall()
    for result in rv:
        content = {'id': result[0], 'firstName': result[1], 'lastName': result[2], 'email': result[3],
                   'username': result[4], 'avatarVersion': result[5], 'canton': result[7]}
    return jsonify(content)


# Get a user by email
@app.route("/getUserByEmail", methods=['GET'])
def getUserByEmail():
    cursor.execute("SELECT * FROM user WHERE email = %s", (request.args.get('email'),))
    rv = cursor.fetchall()
    for result in rv:
        content = {'id': result[0], 'firstName': result[1], 'lastName': result[2], 'email': result[3],
                   'username': result[4], 'avatarVersion': result[5], 'canton': result[7]}
    return jsonify(content)


@app.route("/getTopFiveUsersLabeledCount", methods=['GET'])
def getTopFiveUsersLabeledCount():
    cursor.execute(
        "SELECT user.id, user.username, COUNT(userAndTextAudio.id) FROM userAndTextAudio JOIN user ON user.id = userAndTextAudio.userId GROUP BY user.id")
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {'userId': result[0], 'username': result[1], 'labelCount': result[2]}
        payload.append(content)
        content = {}
    return jsonify(payload)


# Update a user
@app.route("/updateUser", methods=['POST'])
def updateUser():
    cursor.execute(
        "UPDATE user SET firstName = %s, lastName = %s, email = %s, username = %s, avatarVersion = %s, canton = %s WHERE id = %s",
        (request.json['firstName'], request.json['lastName'], request.json['email'],
         request.json['username'], request.json['avatarVersion'], request.json['canton'], request.json['id']))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Delete a user
@app.route("/deleteUser", methods=['DELETE'])
def deleteUser():
    cursor.execute("DELETE FROM user WHERE id = %s", (request.args.get('id'),))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getTextAudio", methods=['GET'])
def getTextAudio():
    cursor.execute("SELECT * FROM textaudio WHERE labeled = 0 group by id asc limit 1")
    rv = cursor.fetchall()
    for result in rv:
        content = {
            'id': result[0],
            'audioStart': result[1],
            'audioEnd': result[2],
            'text': result[3],
            'fileId': result[4],
            'speaker': result[5],
            'labeled': result[6],
            'correct': result[7],
            'wrong': result[8]
        }
    return jsonify(content)


@app.route("/updateTextAudio", methods=['POST'])
def updateTextAudio():
    cursor.execute(
        "UPDATE textaudio SET audioStart = %s, audioEnd = %s, text = %s, labeled = %s, correct = %s, wrong = %s WHERE id = %s",
        (request.json['audioStart'], request.json['audioEnd'], request.json['text'], request.json['labeled'],
         request.json['correct'], request.json['wrong'], request.json['id']))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getTextAudios", methods=['GET'])
def getTextAudios():
    cursor.execute("SELECT * FROM textaudio")
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {
            'id': result[0],
            'audioStart': result[1],
            'audioEnd': result[2],
            'text': result[3],
            'fileId': result[4],
            'speaker': result[5],
            'labeled': result[6],
            'correct': result[7],
            'wrong': result[8]
        }
        payload.append(content)
        content = {}
    return jsonify(payload)


@app.route("/getSpeaker", methods=['GET'])
def getSpeaker():
    cursor.execute("SELECT * FROM speaker WHERE speakerId = %s", (request.args.get('speakerId'),))
    rv = cursor.fetchall()
    for result in rv:
        content = {'id': result[0], 'speakerId': result[1], 'sex': result[2], 'languageUsed': result[3],
                   'dialect': result[4]}
    return jsonify(content)


@app.route("/getTenNonLabeledTextAudios", methods=['GET'])
def getTenNonLabeledTextAudios():
    cursor.execute("SELECT * FROM textAudio where labeled = 0 group by id asc limit 10")
    rv = cursor.fetchall()
    payload = []
    content = {}
    for vi in rv:
        content = {
            'id': vi[0], 'audioStart': vi[1], 'audioEnd': vi[2], 'text': vi[3], 'fileId': vi[4], 'speaker': vi[5],
            'labeled': vi[6], 'correct': vi[7], 'wrong': vi[8]
        }
        payload.append(content)
        content = {}
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


@app.route("/createUserAndTextAudio", methods=['POST'])
def createUserAndTextAudio():
    cursor.execute(
        "INSERT INTO userandtextaudio(userId, textAudioId, time) VALUES(%s, %s, %s)",
        (request.json['userId'], request.json['textAudioId'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
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
    cursor.execute("SELECT COUNT(id) FROM textaudio WHERE correct != 0")
    correct = cursor.fetchone()
    cursor.execute("SELECT COUNT(id) FROM textaudio WHERE wrong != 0")
    wrong = cursor.fetchone()
    cursor.execute("SELECT COUNT(id) FROM textaudio")
    totalTextAudios = cursor.fetchone()
    return jsonify({'correct': correct[0], 'wrong': wrong[0], 'total': totalTextAudios[0]})


# Create avatar
@app.route("/createAvatar", methods=['POST'])
def createAvatar():
    cursor.execute("DELETE FROM avatar WHERE avatar.userId = %s", (request.json['userId'],))
    dataBase.commit()
    cursor.execute("INSERT INTO avatar(userId, avatar) VALUES(%s, %s)",
                   (request.json['userId'], json.dumps(request.json['avatar']),))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get avatar
@app.route("/getAvatar", methods=['GET'])
def getAvatar():
    cursor.execute("SELECT avatar FROM avatar WHERE userId = %s", (request.args.get('userId'),))
    avatar = cursor.fetchall()
    return Response(avatar[0][0], mimetype='image/jpg')


@app.route("/createRecording", methods=['POST'])
def createRecording():
    cursor.execute("INSERT INTO recordings(text, userId, audio) VALUES(%s, %s, %s)",
                   (request.json['text'], request.json['userId'], json.dumps(request.json['audio']),))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getAudio", methods=['GET'])
def getAudio():
    return send_from_directory('C:\\Users\\Jonas\\Documents\\data\\' + request.args.get('id'), 'audio.wav')


if __name__ == '__main__':
    app.run(port=8080)
