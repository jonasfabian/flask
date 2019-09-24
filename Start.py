import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_restful import Api
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)
api = Api(app)
CORS(app)
dataBase = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='password',
    database='labeling-tool'
)
cursor = dataBase.cursor()


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


if __name__ == '__main__':
    app.run(port=8080)
