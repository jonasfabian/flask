from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from flask_login import login_required, login_user, LoginManager
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_mysqldb import MySQL
import json

app = Flask(__name__)
api = Api(app)
app.secret_key = b'myzFrIhsQHIGDWSIHbtIL6QPTGAqvxS5'
app.debug = True

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'labeling-tool'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

loginManager = LoginManager()
loginManager.init_app(app)

bcrypt = Bcrypt(app)

CORS(app)

mysql = MySQL(app)

class User:
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id


@app.route("/login", methods=['POST'])
def login():
    print(request.json)
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE email = %s", (request.json['email'],))
    user = cur.fetchone()
    if user is not None:
        print('yote')
        user = User(user['id'], user['email'], user['password'])
        if bcrypt.check_password_hash(user.password, request.json['password']):
            print('yeet')
            login_user(user)
            return jsonify({'Authenticated': True}), 200
    return jsonify({'Authenticated': False}), 401


@app.route("/changePassword", methods=['POST'])
@login_required
def changePassword():
    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM user WHERE id = %s", (request.json['userId'],))
    oldPassword = cur.fetchone()
    newPassword = bcrypt.generate_password_hash(request.json['newPassword'])
    if bcrypt.check_password_hash(oldPassword['password'], request.json['password']):
        cur.execute("INSERT INTO user(password) VALUES(%s)", newPassword)
        mysql.connection.commit()
        cur.close()
        return jsonify({'Authenticated': True}), 200
    else:
        cur.close()
        return jsonify({'Authenticated': False}), 401


# Create a user
@app.route("/createUser", methods=['POST'])
def createUser():
    pw = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO user(firstName, lastName, email, username, avatarVersion, password, canton) VALUES(%s, %s, %s, %s, %s, %s, %s)",
        (request.json['firstName'], request.json['lastName'], request.json['email'],
         request.json['username'], request.json['avatarVersion'], pw, request.json['canton']))
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get a user by Id
@app.route("/getUserById", methods=['GET'])
@login_required
def getUserById():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE id = %s", (request.args.get('id'),))
    result = cur.fetchone()
    content = {'id': result['id'], 'firstName': result['firstName'], 'lastName': result['lastName'],
               'email': result['email'],
               'username': result['username'], 'avatarVersion': result['avatarVersion'], 'canton': result['canton']}
    cur.close()
    return jsonify(content)


# Get a user by username
@app.route("/getUserByUsername", methods=['GET'])
@login_required
def getUserByUsername():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE username = %s", (request.args.get('username'),))
    rv = cur.fetchone()
    for result in rv:
        content = {'id': result['id'], 'firstName': result['firstName'], 'lastName': result['lastName'],
                   'email': result['email'],
                   'username': result['username'], 'avatarVersion': result['avatarVersion'], 'canton': result['canton']}
    cur.close()
    return jsonify(content)


# Get a user by email
@app.route("/getUserByEmail", methods=['GET'])
def getUserByEmail():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE email = %s", (request.args.get('email'),))
    rv = cur.fetchall()
    content = {}
    for result in rv:
        content = {'id': result['id'], 'firstName': result['firstName'], 'lastName': result['lastName'],
                   'email': result['email'],
                   'username': result['username'], 'avatarVersion': result['avatarVersion'], 'canton': result['canton']}
    cur.close()
    return jsonify(content)


# Update a user
@app.route("/updateUser", methods=['POST'])
@login_required
def updateUser():
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE user SET firstName = %s, lastName = %s, email = %s, username = %s, avatarVersion = %s, canton = %s WHERE id = %s",
        (request.json['firstName'], request.json['lastName'], request.json['email'],
         request.json['username'], request.json['avatarVersion'], request.json['canton'], request.json['id']), )
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Delete a user
@app.route("/deleteUser", methods=['DELETE'])
@login_required
def deleteUser():
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM user WHERE id = %s", (request.args.get('id'),))
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getTextAudio", methods=['GET'])
@login_required
def getTextAudio():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM textAudio WHERE labeled = 0 group by id asc limit 1")
    rv = cur.fetchall()
    for result in rv:
        content = {
            'id': result['id'],
            'audioStart': result['audioStart'],
            'audioEnd': result['audioEnd'],
            'text': result['text'],
            'fileId': result['fileId'],
            'speaker': result['speaker'],
            'labeled': result['labeled'],
            'correct': result['correct'],
            'wrong': result['wrong']
        }
    cur.close()
    return jsonify(content)


@app.route("/updateTextAudio", methods=['POST'])
@login_required
def updateTextAudio():
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE textAudio SET audioStart = %s, audioEnd = %s, text = %s, labeled = %s, correct = %s, wrong = %s WHERE id = %s",
        (request.json['audioStart'], request.json['audioEnd'], request.json['text'], request.json['labeled'],
         request.json['correct'], request.json['wrong'], request.json['id']), )
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getTextAudios", methods=['GET'])
@login_required
def getTextAudios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM textAudio")
    rv = cur.fetchall()
    payload = []
    for result in rv:
        content = {
            'id': result['id'],
            'audioStart': result['audioStart'],
            'audioEnd': result['audioEnd'],
            'text': result['text'],
            'fileId': result['fileId'],
            'speaker': result['speaker'],
            'labeled': result['labeled'],
            'correct': result['correct'],
            'wrong': result['wrong']
        }
        payload.append(content)
    cur.close()
    return jsonify(payload)


@app.route("/getSpeaker", methods=['GET'])
@login_required
def getSpeaker():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM speaker WHERE speakerId = %s", (request.args.get('speakerId'),))
    rv = cur.fetchall()
    for result in rv:
        content = {'id': result['id'], 'speakerId': result['speakerId'], 'sex': result['sex'],
                   'languageUsed': result['languageUsed'],
                   'dialect': result['dialect']}
    cur.close()
    return jsonify(content)


@app.route("/getTenNonLabeledTextAudios", methods=['GET'])
@login_required
def getTenNonLabeledTextAudios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM textAudio where labeled = 0 group by id asc limit 10")
    rv = cur.fetchall()
    payload = []
    for vi in rv:
        content = {
            'id': vi['id'], 'audioStart': vi['audioStart'], 'audioEnd': vi['audioEnd'], 'text': vi['text'],
            'fileId': vi['fileId'], 'speaker': vi['speaker'],
            'labeled': vi['labeled'], 'correct': vi['correct'], 'wrong': vi['wrong']
        }
        payload.append(content)
    cur.close()
    return jsonify(payload)


# Get textAudioIndex by labeled type
@app.route("/getTextAudioIndexesByLabeledType", methods=['GET'])
@login_required
def getTextAudioIndexesByLabeledType():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM textAudioIndex WHERE labeled = %s", (request.args.get('labeledType'),))
    rv = cur.fetchall()
    payload = []
    for result in rv:
        content = {
            'id': result['id'], 'samplingRate': result['samplingRate'], 'textStartPos': result['textStartPos'],
            'textEndPos': result['textEndPos'],
            'audioStartPos': result['audioStartPos'], 'audioEndPos': result['audioEndPos'],
            'speakerKey': result['speakerKey'], 'labeled': result['labeled'],
            'correct': result['correct'], 'wrong': result['wrong'], 'transcript_file_id': result['transcript_file_id']
        }
        payload.append(content)
    cur.close()
    return jsonify(payload)


@app.route("/createUserAndTextAudio", methods=['POST'])
@login_required
def createUserAndTextAudio():
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO userAndTextAudio(userId, textAudioId, time) VALUES(%s, %s, %s)",
        (request.json['userId'], request.json['textAudioId'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'),))
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get top five users by labeling amount
@app.route("/getTopFive", methods=['GET', 'OPTIONS'])
@login_required
def getTopFive():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT user.id, user.username, COUNT(userAndTextAudio.userId) FROM userAndTextAudio JOIN user ON user.id = userAndTextAudio.userId GROUP BY user.id LIMIT 5")
    rv = cur.fetchall()
    payload = []
    for result in rv:
        content = {
            'id': result['id'], 'username': result['username'], 'count': result['COUNT(userAndTextAudio.userId)']
        }
        payload.append(content)
    cur.close()
    return jsonify(payload)


# Get sums of labeled
@app.route("/getLabeledSums", methods=['GET'])
@login_required
def getLabeledSums():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(id) FROM textAudio WHERE correct != 0")
    correct = cur.fetchone()
    cur.execute("SELECT COUNT(id) FROM textAudio WHERE wrong != 0")
    wrong = cur.fetchone()
    cur.execute("SELECT COUNT(id) FROM textAudio")
    total = cur.fetchone()
    cur.close()
    return jsonify({'correct': correct['COUNT(id)'], 'wrong': wrong['COUNT(id)'], 'total': total['COUNT(id)']})


# Create avatar
@app.route("/createAvatar", methods=['POST'])
@login_required
def createAvatar():
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM avatar WHERE avatar.userId = %s", (request.json['userId'],))
    mysql.connection.commit()
    cur.execute("INSERT INTO avatar(userId, avatar) VALUES(%s, %s)",
                (request.json['userId'], json.dumps(request.json['avatar'])))
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


# Get avatar
@app.route("/getAvatar", methods=['GET'])
@login_required
def getAvatar():
    cur = mysql.connection.cursor()
    cur.execute("SELECT avatar FROM avatar WHERE userId = %s", (request.args.get('userId'),))
    avatar = cur.fetchone()
    cur.close()
    return Response(avatar['avatar'], mimetype='image/jpg')


@app.route("/createRecording", methods=['POST'])
@login_required
def createRecording():
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO recordings(text, userId, audio) VALUES(%s, %s, %s)",
                (request.json['text'], request.json['userId'], json.dumps(request.json['audio']),))
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getAudio", methods=['GET', 'OPTIONS'])
@login_required
def getAudio():
    return send_from_directory('C:\\Users\\Jonas\\Documents\\data\\' + request.args.get('id'), 'audio.wav')


@loginManager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE id = %s", (user_id,))
    usr = cur.fetchone()
    if usr is not None:
        return User(usr['id'], usr['email'], usr['password'])
    else:
        return None


def get_user_for_login_data(email, password):
    user = User
    user.email = email
    user.password = password
    return user


if __name__ == '__main__':
    app.run(port=8080)
