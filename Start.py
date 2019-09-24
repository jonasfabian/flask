import mysql.connector
import User
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_login import LoginManager
from flask_restful import Api
from flask_bcrypt import Bcrypt

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


@app.route("/authenticated", methods=['POST'])
def authenticated():
    user = User
    return jsonify(
        {'Authenticated': user.User.is_authenticated(app, bcrypt, request.json['username'], request.json['password'])})


# Create a user
@app.route("/createUser", methods=['POST'])
def createUser():
    pw = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
    cursor.execute(
        "INSERT INTO user(id, firstName, lastName, email, username, avatarVersion, password) VALUES(%s, %s, %s, %s, %s, %s, %s)",
        (request.json['id'], request.json['firstName'], request.json['lastName'], request.json['email'],
         request.json['username'], request.json['avatarVersion'], pw))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get a user
@app.route("/getUser", methods=['GET'])
def getUserById():
    cursor.execute("SELECT * FROM user WHERE id = %s", (request.args.get('id'),))
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {'id': result[0], 'firstName': result[1], 'lastName': result[2], 'email': result[3],
                   'username': result[4], 'avatarVersion': result[5]}
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


# Create a textAudioIndex
@app.route("/createTextAudioIndex", methods=['POST'])
def createTextAudioIndex():
    cursor.execute(
        "INSERT INTO textAudioIndex(samplingRate, textStartPos, textEndPos, audioStartPos, audioEndPos, speakerKey, labeled, correct, wrong, transcript_file_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (request.json['samplingRate'], request.json['textStartPos'], request.json['textEndPos'],
         request.json['audioStartPos'], request.json['audioEndPos'], request.json['speakerKey'],
         request.json['labeled'], request.json['correct'], request.json['wrong'], request.json['transcript_file_id']))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get a textAudioIndex
@app.route("/getTextAudioIndex", methods=['GET'])
def getTextAudioIndexes():
    cursor.execute("SELECT * FROM textAudioIndex WHERE id = %s", (request.args.get('id'),))
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


# Update a textAudioIndex
@app.route("/updateTextAudioIndex", methods=['PUT'])
def updateTextAudioIndex():
    cursor.execute(
        "INSERT INTO textAudioIndex(samplingRate, textStartPos, textEndPos, audioStartPos, audioEndPos, speakerKey, labeled, correct, wrong, transcript_file_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) WHERE id = %s",
        (request.json['samplingRate'], request.json['textStartPos'], request.json['textEndPos'],
         request.json['audioStartPos'], request.json['audioEndPos'], request.json['speakerKey'],
         request.json['labeled'], request.json['correct'], request.json['wrong'], request.json['transcript_file_id'],
         request.json['id']))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Delete a textAudioIndex
@app.route("/deleteTextAudioIndex", methods=['DELETE'])
def deleteTextAudioIndex():
    cursor.execute("DELETE FROM textAudioIndex WHERE id = %s", (request.args.get('id'),))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Create a userAndTextAudioIndex
@app.route("/createUserAndTextAudioIndex", methods=['POST'])
def userAndTextAudioIndex():
    cursor.execute(
        "INSERT INTO userAndTextAudioIndex(userId, textAudioIndexId, time) VALUES(%s, %s, %s)",
        (request.json['userId'], request.json['textAudioIndexId'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    dataBase.commit()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get a textAudioIndex by user
@app.route("/getUserAndTextAudioIndexByUser", methods=['GET'])
def getUserAndTextAudioIndexByUser():
    cursor.execute(
        "SELECT textAudioIndex.* FROM textAudioIndex JOIN userAndTextAudioIndex ON textAudioIndex.id = userAndTextAudioIndex.textAudioIndexId AND userAndTextAudioIndex.userId = %s",
        (request.args.get('id'),))
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


# Get top five users by labeling amount
@app.route("/getTopFive", methods=['GET'])
def getTopFiveUsersByLabelCount():
    cursor.execute(
        "SELECT user.id, user.username, count(userAndTextAudioIndex.userId) FROM userAndTextAudioIndex JOIN user ON user.id = userAndTextAudioIndex.userId GROUP BY user.id LIMIT 5")
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {
            'id': result[0], 'username': result[1], 'count': result[2]
        }
        payload.append(content)
        content = {}
    return jsonify(payload)


if __name__ == '__main__':
    app.run(port=8080)
