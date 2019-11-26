import json
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory, redirect
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import login_user, LoginManager
from flask_mysqldb import MySQL
from flask_restful import Api

from config import baseDir, user, passwd, database

app = Flask(__name__,
            static_folder='static/public/'
            )
api = Api(app)
app.secret_key = b'myzFrIhsQHIGDWSIHbtIL6QPTGAqvxS5'
app.url_map.strict_slashes = True
app.debug = True

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = user
app.config['MYSQL_PASSWORD'] = passwd
app.config['MYSQL_DB'] = database
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


@app.route("/app")
def forwardToAngular():
    return redirect("/speech-to-text-labeling-tool/app/index.html")


@app.route("/login", methods=['POST'])
def login():
    cur = mysql.connection.cursor()
    user = cur.fetchone()
    if user is not None:
        user = User(user['id'], user['email'], user['password'])
        if bcrypt.check_password_hash(user.password, request.json['password']):
            login_user(user)
            return jsonify({'Authenticated': True}), 200
    return jsonify({'Authenticated': False}), 401


def login_required(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        user = None
        if auth is not None:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM user WHERE email = %s", [auth.username])
            user = cur.fetchone()
        if user is not None:
            if not bcrypt.check_password_hash(user['password'], auth.password):
                return ('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(**kwargs)

    return wrapped_view


@app.route("/changePassword", methods=['POST'])
@login_required
def changePassword():
    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM user WHERE id = %s", [request.json['userId']])
    oldPassword = cur.fetchone()
    newPassword = bcrypt.generate_password_hash(request.json['newPassword'])
    if bcrypt.check_password_hash(oldPassword['password'], request.json['password']):
        cur.execute("UPDATE user set password = %s where user.id = %s", [newPassword, request.json['userId']])
        mysql.connection.commit()
        cur.close()
        return jsonify({'Authenticated': True}), 200
    else:
        cur.close()
        return jsonify({'Authenticated': False}), 400


@app.route("/createUser", methods=['POST'])
def createUser():
    pw = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO user(firstName, lastName, email, username,  password, canton) VALUES(%s, %s, %s, %s, %s, %s)",
        [request.json['firstName'], request.json['lastName'], request.json['email'], request.json['username'],
         pw, request.json['canton']])
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getUserByEmail", methods=['GET'])
def getUserByEmail():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE email = %s", [request.args.get('email'), ])
    result = cur.fetchone()
    if result is not None:
        result = {'id': result['id'], 'firstName': result['firstName'], 'lastName': result['lastName'],
                  'email': result['email'], 'username': result['username'],
                  'canton': result['canton']}
    cur.close()
    return jsonify(result)


@app.route("/updateUser", methods=['POST'])
@login_required
def updateUser():
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE user SET firstName = %s, lastName = %s, email = %s, username = %s,  canton = %s WHERE id = %s",
        [request.json['firstName'], request.json['lastName'], request.json['email'], request.json['username'],
         request.json['canton'], request.json['id']], )
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/updateTextAudio", methods=['POST'])
@login_required
def updateTextAudio():
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE textAudio SET audioStart = %s, audioEnd = %s, text = %s, labeled = %s, correct = %s, wrong = %s WHERE id = %s",
        [request.json['audioStart'], request.json['audioEnd'], request.json['text'], request.json['labeled'],
         request.json['correct'], request.json['wrong'], request.json['id']], )
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
        content = {'id': result['id'], 'audioStart': result['audioStart'], 'audioEnd': result['audioEnd'],
                   'text': result['text'], 'fileId': result['fileId'], 'speaker': result['speaker'],
                   'labeled': result['labeled'], 'correct': result['correct'], 'wrong': result['wrong']}
        payload.append(content)
    cur.close()
    return jsonify(payload)


@app.route("/getTenNonLabeledTextAudios", methods=['GET'])
@login_required
def getTenNonLabeledTextAudios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM textAudio where labeled = 0 group by id asc limit 10")
    rv = cur.fetchall()
    payload = []
    for vi in rv:
        content = {'id': vi['id'], 'audioStart': vi['audioStart'], 'audioEnd': vi['audioEnd'], 'text': vi['text'],
                   'fileId': vi['fileId'], 'speaker': vi['speaker'], 'labeled': vi['labeled'], 'correct': vi['correct'],
                   'wrong': vi['wrong']}
        payload.append(content)
    cur.close()
    return jsonify(payload)


@app.route("/createUserAndTextAudio", methods=['POST'])
@login_required
def createUserAndTextAudio():
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO userAndTextAudio(userId, textAudioId, time) VALUES(%s, %s, %s)",
                [request.json['userId'], request.json['textAudioId'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ])
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getTopFive", methods=['GET', 'OPTIONS'])
@login_required
def getTopFive():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT user.id, user.username, COUNT(userAndTextAudio.userId) FROM userAndTextAudio JOIN user ON user.id = userAndTextAudio.userId GROUP BY user.id LIMIT 5")
    rv = cur.fetchall()
    payload = []
    for result in rv:
        content = {'id': result['id'], 'username': result['username'],
                   'count': result['COUNT(userAndTextAudio.userId)']}
        payload.append(content)
    cur.close()
    return jsonify(payload)


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


@app.route("/createRecording", methods=['POST'])
@login_required
def createRecording():
    cur = mysql.connection.cursor()
    data = json.loads(request.form['data'])
    cur.execute("INSERT INTO recordings(text, userId, audio) VALUES(%s, %s, %s)",
                [data['text'], data['userId'], request.files['file'].read(), ])
    mysql.connection.commit()
    cur.close()
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.route("/getRecordingDataById", methods=['GET'])
@login_required
def getRecordingDataById():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, text, userId FROM recordings WHERE id = %s",
                [request.args.get('id')])
    recording = cur.fetchone()
    cur.close()
    return jsonify({'id': recording['id'], 'text': recording['text'], 'userId': recording['userId']})


@app.route("/getAllRecordingData", methods=['GET'])
@login_required
def getAllRecordingData():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, text, userId FROM recordings", )
    recording = cur.fetchall()
    cur.close()
    payload = []
    for record in recording:
        print(record)
        payload.append(record)
    return jsonify(payload)


@app.route("/getRecordingAudioById", methods=['GET'])
@login_required
def getRecordingAudioById():
    cur = mysql.connection.cursor()
    cur.execute("SELECT audio FROM recordings WHERE id = %s",
                [request.args.get('id')])
    audio = cur.fetchone()
    cur.close()
    return Response(audio['audio'], mimetype='audio/webm;codecs=opus')


@app.route("/getAudio", methods=['GET', 'OPTIONS'])
@login_required
def getAudio():
    return send_from_directory(baseDir + request.args.get('id'), 'audio.wav')


@loginManager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE id = %s", user_id)
    usr = cur.fetchone()
    if usr is not None:
        usr = User(usr['id'], usr['email'], usr['password'])
    return usr


if __name__ == '__main__':
    app.run(port=8080)
