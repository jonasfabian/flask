import mysql.connector
import user
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
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
    userr = user
    return jsonify(
        {'Authenticated': userr.User.is_authenticated(app, bcrypt, request.json['username'], request.json['password'])})


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


# Get a user by Id
@app.route("/getUserById", methods=['GET'])
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


# Get a user by username
@app.route("/getUserByUsername", methods=['GET'])
def getUserByUsername():
    cursor.execute("SELECT * FROM user WHERE username = %s", (request.args.get('username'),))
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {'id': result[0], 'firstName': result[1], 'lastName': result[2], 'email': result[3],
                   'username': result[4], 'avatarVersion': result[5]}
        payload.append(content)
        content = {}
    return jsonify(payload)


# Get a user by email
@app.route("/getUserByEmail", methods=['GET'])
def getUserByEmail():
    cursor.execute("SELECT * FROM user WHERE email = %s", (request.args.get('email'),))
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {'id': result[0], 'firstName': result[1], 'lastName': result[2], 'email': result[3],
                   'username': result[4], 'avatarVersion': result[5]}
        payload.append(content)
        content = {}
    return jsonify(payload)


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
def getTextAudioIndex():
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


# Get all textAudioIndex
@app.route("/getTextAudioIndexes", methods=['GET'])
def getTextAudioIndexes():
    cursor.execute("SELECT * FROM textAudioIndex")
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


# Update a textAudioIndex
@app.route("/updateTextAudioIndex", methods=['PUT'])
def updateTextAudioIndex():
    cursor.execute(
        """INSERT INTO textAudioIndex(
        samplingRate,
        textStartPos,
        textEndPos,
        audioStartPos,
        audioEndPos,
        speakerKey,
        labeled,
        correct,
        wrong,
        transcript_file_id
        ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) WHERE id = %s""",
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
def createUserAndTextAudioIndex():
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


# Get ten not yet labeled textAudioIndexes by user
@app.route("/getTenNonLabeledDataIndexesByUser", methods=['GET'])
def getTenNonLabeledDataIndexesByUser():
    cursor.execute(
        "SELECT textAudioIndex.id FROM textAudioIndex JOIN userAndTextAudioIndex ON userAndTextAudioIndex.textAudioIndexId = textAudioIndex.id AND userAndTextAudioIndex.userId = %s",
        (request.args.get('id'),))
    ids = cursor.fetchall()
    payload = []
    content = {}
    for id in ids:
        cursor.execute(
            "SELECT textAudioIndex.id, "
            "textAudioIndex.samplingRate, "
            "textAudioIndex.textStartPos, "
            "textAudioIndex.textEndPos, "
            "textAudioIndex.audioStartPos, "
            "textAudioIndex.audioEndPos, "
            "textAudioIndex.speakerKey, "
            "textAudioIndex.labeled, "
            "textAudioIndex.correct, "
            "textAudioIndex.wrong, "
            "transcript.fileId, "
            "transcript.text FROM textAudioIndex "
            "JOIN transcript ON textAudioIndex.transcript_file_id = transcript.fileId WHERE textAudioIndex.id != %s LIMIT 10",
            (id[0],))
        vi = cursor.fetchall()
        content = {
            'id': vi[0][0], 'samplingRate': vi[0][1], 'textStartPos': vi[0][2], 'textEndPos': vi[0][3],
            'audioStartPos': vi[0][4], 'audioEndPos': vi[0][5], 'speakerKey': vi[0][6], 'labeled': vi[0][7],
            'correct': vi[0][8], 'wrong': vi[0][9], 'fileId': vi[0][10], 'text': vi[0][11]
        }
        payload.append(content)
        content = {}
    print(payload)
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


# Get Transcripts
@app.route("/getTranscripts", methods=['GET'])
def getTranscripts():
    cursor.execute("SELECT * FROM transcript")
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {
            'id': result[0], 'text': result[1], 'fileId': result[2]
        }
        payload.append(content)
        content = {}
    return jsonify(payload)


# Get Transcript by Id
@app.route("/getTranscript", methods=['GET'])
def getTranscriptById():
    cursor.execute("SELECT * FROM transcript WHERE id = %s", (request.args.get('id'),))
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {
            'id': result[0], 'text': result[1], 'fileId': result[2]
        }
        payload.append(content)
        content = {}
    return jsonify(payload)


# Get Transcript by Id
@app.route("/getAudio", methods=['GET'])
def getAudio():
    cursor.execute("SELECT * FROM audio WHERE fileId = %s", (request.args.get('fileId'),))
    rv = cursor.fetchall()
    payload = []
    content = {}
    for result in rv:
        content = {
            'id': result[0], 'path': result[1], 'fileId': result[2]
        }
        payload.append(content)
        content = {}
    return jsonify(payload)


# Get audio file
@app.route("/getAudioFile", methods=['GET'])
def getAudioFile():
    path = "/home/jonas/Documents/DeutschAndreaErzaehlt/" + request.args.get('fileId')
    return send_from_directory(path, 'audio.mp3')


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
