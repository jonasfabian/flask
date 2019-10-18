import mysql.connector
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from flask_login import LoginManager
from flask_restful import Api
from flask_bcrypt import Bcrypt
import json
from configuration import *
import user

app = Flask(__name__)
api = Api(app)
app.secret_key = b'myzFrIhsQHIGDWSIHbtIL6QPTGAqvxS5'
app.debug = True

loginManager = LoginManager()
loginManager.init_app(app)

bcrypt = Bcrypt(app)

CORS(app)
dataBase = mysql.connector.connect(
    host='localhost',
    user='flask',
    passwd='flask',
    database='labeling-tool'
)


def fetchall(operation, params=()):
    cursor = dataBase.cursor()
    cursor.execute(operation=operation, params=params, multi=False)
    fetchall = cursor.fetchall()
    cursor.close()
    return fetchall


def fetchone(operation, params=()):
    fetchalll = fetchall(operation, params)
    if fetchalll:
        return fetchalll[0]
    else:
        return None


def autocommit(operation, params=()):
    cursor = dataBase.cursor()
    cursor.execute(operation=operation, params=params, multi=False)
    dataBase.commit()


@app.route("/checkLogin", methods=['POST'])
def checkLogin():
    userr = user
    return jsonify(
        {'Authenticated': userr.User.is_authenticated(app, bcrypt, request.json['email'], request.json['password'])})


# Create a user
@app.route("/createUser", methods=['POST'])
def createUser():
    pw = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
    autocommit(
        "INSERT INTO user(firstName, lastName, email, username, avatarVersion, password, canton) VALUES(%s, %s, %s, %s, %s, %s, %s)",
        (request.json['firstName'], request.json['lastName'], request.json['email'],
         request.json['username'], request.json['avatarVersion'], pw, request.json['canton']))
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get a user by Id
@app.route("/getUserById", methods=['GET'])
def getUserById():
    result = fetchone("SELECT * FROM user WHERE id = %s", (request.args.get('id'),))
    content = {'id': result[0], 'firstName': result[1], 'lastName': result[2], 'email': result[3],
               'username': result[4], 'avatarVersion': result[5], 'canton': result[7]}
    return jsonify(content)


# Get a user by username
@app.route("/getUserByUsername", methods=['GET'])
def getUserByUsername():
    rv = fetchall("SELECT * FROM user WHERE username = %s", (request.args.get('username'),))
    for result in rv:
        content = {'id': result[0], 'firstName': result[1], 'lastName': result[2], 'email': result[3],
                   'username': result[4], 'avatarVersion': result[5], 'canton': result[7]}
    return jsonify(content)


# Get a user by email
@app.route("/getUserByEmail", methods=['GET'])
def getUserByEmail():
    rv = fetchall("SELECT * FROM user WHERE email = %s", (request.args.get('email'),))
    content = None
    for result in rv:
        content = {'id': result[0], 'firstName': result[1], 'lastName': result[2], 'email': result[3],
                   'username': result[4], 'avatarVersion': result[5], 'canton': result[7]}
    return jsonify(content)


@app.route("/getTopFiveUsersLabeledCount", methods=['GET'])
def getTopFiveUsersLabeledCount():
    rv = fetchall(
        "SELECT user.id, user.username, COUNT(userAndTextAudio.id) FROM userAndTextAudio JOIN user ON user.id = userAndTextAudio.userId GROUP BY user.id")
    payload = []
    for result in rv:
        content = {'userId': result[0], 'username': result[1], 'labelCount': result[2]}
        payload.append(content)
    return jsonify(payload)


# Update a user
@app.route("/updateUser", methods=['POST'])
def updateUser():
    autocommit(
        "UPDATE user SET firstName = %s, lastName = %s, email = %s, username = %s, avatarVersion = %s, canton = %s WHERE id = %s",
        (request.json['firstName'], request.json['lastName'], request.json['email'],
         request.json['username'], request.json['avatarVersion'], request.json['canton'], request.json['id']))
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Delete a user
@app.route("/deleteUser", methods=['DELETE'])
def deleteUser():
    autocommit("DELETE FROM user WHERE id = %s", (request.args.get('id'),))
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getTextAudio", methods=['GET'])
def getTextAudio():
    rv = fetchall("SELECT * FROM textAudio WHERE labeled = 0 group by id asc limit 1")
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
    autocommit(
        "UPDATE textAudio SET audioStart = %s, audioEnd = %s, text = %s, labeled = %s, correct = %s, wrong = %s WHERE id = %s",
        (request.json['audioStart'], request.json['audioEnd'], request.json['text'], request.json['labeled'],
         request.json['correct'], request.json['wrong'], request.json['id']))
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getTextAudios", methods=['GET'])
def getTextAudios():
    rv = fetchall("SELECT * FROM textAudio LIMIT 10")
    payload = []
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
    return jsonify(payload)


@app.route("/getSpeaker", methods=['GET'])
def getSpeaker():
    rv = fetchall("SELECT * FROM speaker WHERE speakerId = %s", (request.args.get('speakerId'),))
    for result in rv:
        content = {'id': result[0], 'speakerId': result[1], 'sex': result[2], 'languageUsed': result[3],
                   'dialect': result[4]}
    return jsonify(content)


@app.route("/getTenNonLabeledTextAudios", methods=['GET'])
def getTenNonLabeledTextAudios():
    rv = fetchall("SELECT * FROM textAudio where labeled = 0 group by id asc limit 10")
    payload = []
    for vi in rv:
        content = {
            'id': vi[0], 'audioStart': vi[1], 'audioEnd': vi[2], 'text': vi[3], 'fileId': vi[4], 'speaker': vi[5],
            'labeled': vi[6], 'correct': vi[7], 'wrong': vi[8]
        }
        payload.append(content)
    return jsonify(payload)


# Get textAudioIndex by labeled type
@app.route("/getTextAudioIndexesByLabeledType", methods=['GET'])
def getTextAudioIndexesByLabeledType():
    rv = fetchall("SELECT * FROM textAudioIndex WHERE labeled = %s", (request.args.get('labeledType'),))
    payload = []
    for result in rv:
        content = {
            'id': result[0], 'samplingRate': result[1], 'textStartPos': result[2], 'textEndPos': result[3],
            'audioStartPos': result[4], 'audioEndPos': result[5], 'speakerKey': result[6], 'labeled': result[6],
            'correct': result[7], 'wrong': result[8], 'transcript_file_id': result[9]
        }
        payload.append(content)
    return jsonify(payload)


@app.route("/createUserAndTextAudio", methods=['POST'])
def createUserAndTextAudio():
    autocommit(
        "INSERT INTO userAndTextAudio(userId, textAudioId, time) VALUES(%s, %s, %s)",
        (request.json['userId'], request.json['textAudioId'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get top five users by labeling amount
@app.route("/getTopFive", methods=['GET', 'OPTIONS'])
def getTopFiveUsersByLabelCount():
    rv = fetchall(
        "SELECT user.id, user.username, count(userAndTextAudio.userId) FROM userAndTextAudio JOIN user ON user.id = userAndTextAudio.userId GROUP BY user.id LIMIT 5")
    payload = []
    for result in rv:
        content = {
            'id': result[0], 'username': result[1], 'count': result[2]
        }
        payload.append(content)
    return jsonify(payload)


# Get sums of labeled
@app.route("/getLabeledSums", methods=['GET'])
def getLabeledSums():
    correct = fetchone("SELECT COUNT(id) FROM textAudio WHERE correct != 0")
    wrong = fetchone("SELECT COUNT(id) FROM textAudio WHERE wrong != 0")
    total = fetchone("SELECT COUNT(id) FROM textAudio")
    return jsonify({'correct': correct[0], 'wrong': wrong[0], 'total': total[0]})


# Create avatar
@app.route("/createAvatar", methods=['POST'])
def createAvatar():
    autocommit("DELETE FROM avatar WHERE avatar.userId = %s", (request.json['userId'],))
    autocommit("INSERT INTO avatar(userId, avatar) VALUES(%s, %s)",
               (request.json['userId'], json.dumps(request.json['avatar']),))
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get avatar
@app.route("/getAvatar", methods=['GET'])
def getAvatar():
    avatar = fetchall("SELECT avatar FROM avatar WHERE userId = %s", (request.args.get('userId'),))
    return Response(avatar[0][0], mimetype='image/jpg')


@app.route("/createRecording", methods=['POST'])
def createRecording():
    autocommit("INSERT INTO recordings(text, userId, audio) VALUES(%s, %s, %s)",
               (request.json['text'], request.json['userId'], json.dumps(request.json['audio']),))
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getAudio", methods=['GET'])
def getAudio():
    return send_from_directory(dirSlash + request.args.get('id'), 'audio.wav')


if __name__ == '__main__':
    app.run(port=8080)
