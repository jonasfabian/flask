import json
import os
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory, redirect, Response, session
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import login_user, LoginManager, current_user
from flask_mysqldb import MySQL
from flask_restful import Api

from src.config import baseDir, db_1_user, db_1_pw, database_1
from src.speech_to_text_datastore import SpeechToTextDatastore

app = Flask(__name__,
            static_folder='static/public/'
            )
api = Api(app)
app.secret_key = b'myzFrIhsQHIGDWSIHbtIL6QPTGAqvxS5'
app.url_map.strict_slashes = True
app.debug = True

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = db_1_user
app.config['MYSQL_PASSWORD'] = db_1_pw
app.config['MYSQL_DB'] = database_1
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

loginManager = LoginManager()
loginManager.init_app(app)

bcrypt = Bcrypt(app)

CORS(app)

mysql = MySQL(app)
datastore = SpeechToTextDatastore()
ACCESS_LEVEL = {
    'user': 0,
    'group_admin': 1,
    'admin': 2
}


class User:
    def __init__(self, id, email, password, access=ACCESS_LEVEL['user'], group=0):
        self.id = id
        self.email = email
        self.password = password
        self.access = access
        # NOTE this could be replaced with a dict once we have more than one group
        self.group = group

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.id

    def allowed_level(self, access_level):
        return self.access >= access_level

    def allowed_group(self, group):
        return self.group == group


def success():
    return jsonify({'success': True}), 200, {'ContentType': 'application/json'}


@app.errorhandler(404)
def page_not_fond(e):
    return redirect("/speech-to-text-labeling-tool/app/index.html")


# NOTE flask does not support forwarding requests to the index.html
@app.route("/app")
def forwardToAngular():
    return redirect("/speech-to-text-labeling-tool/app/index.html")


# FIXME this does not do anything? see login_required
@app.route("/login", methods=['POST'])
def login():
    print("login: user logged in check")
    cur = mysql.connection.cursor()
    if '@' in request.json['email']:
        cur.execute("SELECT * FROM user WHERE email = %s", [request.json['email']])
    else:
        cur.execute("SELECT * FROM user WHERE username = %s", [request.json['email']])
    user = cur.fetchone()
    if user is not None:
        user = User(user['id'], user['email'], user['password'])
        if bcrypt.check_password_hash(user.password, request.json['password']):
            login_user(user)
            print("login: user logged in")
            return jsonify({'Authenticated': True}), 200
    print("user not logged in")
    return jsonify({'Authenticated': False}), 401


def login_required(f):
    @wraps(f)
    def wrapped_view(**kwargs):
        auth = request.authorization
        user = None
        if auth is not None:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM user WHERE username = %s", [auth.username])
            user = cur.fetchone()
        if user is not None:
            if bcrypt.check_password_hash(user['password'], auth.password):
                user = User(user['id'], user['email'], user['password'])
                login_user(user)
                print("basic auth user checked")
                return f(**kwargs)
        print("basic auth unauthorized")
        return ('Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

    return wrapped_view


@app.route("/api/user", methods=['GET'])
@login_required
def get_user():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE id = %s", [current_user.id])
    result = cur.fetchone()
    if result is not None:
        result = {'id': result['id'], 'firstName': result['first_name'], 'lastName': result['last_name'],
                  'email': result['email'], 'username': result['username'], 'canton': result['canton']}
    return jsonify(result)


@app.route("/api/user", methods=['POST'])
def post_user():
    # TODO not sure how to handle public registration logins
    if '@' in request.json['username']:
        return jsonify({'success': False}), 406
    else:
        pw = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
        cur = mysql.connection.cursor()
        # TODO add additional fields
        cur.execute(
            "INSERT INTO user(first_name, last_name, email, username,  password, canton) VALUES(%s, %s, %s, %s, %s, %s)",
            [request.json['firstName'], request.json['lastName'], request.json['email'], request.json['username'],
             pw, request.json['canton']])
        mysql.connection.commit()
        return success()


@app.route("/api/recording", methods=['POST'])
@login_required
def post_recording():
    cur = mysql.connection.cursor()
    data = json.loads(request.form['data'])
    cur.execute("INSERT INTO recording( user_id, excerpt_id,audio, time) VALUES(%s,%s,%s,%s)",
                [current_user.id, data['excerpt_id'], request.files['file'].read(),
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ])
    mysql.connection.commit()
    return success()


# TODO update method to reflect new architecture
@app.route("/api/excerpt", methods=['GET'])
@login_required
def get_excerpt():
    cur = mysql.connection.cursor()
    # TODO limit based on what was already labeled by user or based on dialect .
    cur.execute("SELECT * FROM excerpt WHERE skipped<3 AND private<1 LIMIT 1 ")
    return jsonify(cur.fetchone())


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
        return jsonify({'Authenticated': True}), 200
    else:
        return jsonify({'Authenticated': False}), 400


@app.route("/updateUser", methods=['POST'])
@login_required
def updateUser():
    if '@' in request.json['username']:
        return jsonify({'success': False}), 406
    else:
        cur = mysql.connection.cursor()
        cur.execute(
            "UPDATE user SET first_name = %s, last_name = %s, email = %s, username = %s,  canton = %s WHERE id = %s",
            [request.json['firstName'], request.json['lastName'], request.json['email'], request.json['username'],
             request.json['canton'], request.json['id']], )
        mysql.connection.commit()
        return success()


# TODO change data structure so each user annotation is separated
@app.route("/updateTextAudio", methods=['POST'])
@login_required
def updateTextAudio():
    cur = mysql.connection.cursor()
    cur.execute(
        "UPDATE text_audio SET audio_start = %s, audio_end = %s, text = %s, labeled = %s, correct = %s, wrong = %s WHERE id = %s",
        [request.json['audioStart'], request.json['audioEnd'], request.json['text'], request.json['labeled'],
         request.json['correct'], request.json['wrong'], request.json['id']], )
    mysql.connection.commit()
    return success()


@app.route("/createUserAndTextAudio", methods=['POST'])
@login_required
def createUserAndTextAudio():
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO user_and_text_audio(user_id, text_audio_id, time) VALUES(%s, %s, %s)",
                [request.json['userId'], request.json['textAudioId'], datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ])
    mysql.connection.commit()
    return success()


# TODO remove this method
@app.route("/updateRecording", methods=['POST'])
@login_required
def updateRecording():
    cur = mysql.connection.cursor()
    # cur.execute(
    #     "UPDATE recordings SET recordings.text = %s WHERE recordings.id = %s", [request.json['text'],
    #                                                                             request.json['id']])
    mysql.connection.commit()
    return success()


# TODO replace with view for aggregated data
@app.route("/getTextAudios", methods=['GET'])
@login_required
def getTextAudios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM text_audio")
    rv = cur.fetchall()
    payload = []
    for result in rv:
        content = {'id': result['id'], 'audioStart': result['audioStart'], 'audioEnd': result['audioEnd'],
                   'text': result['text'], 'fileId': result['fileId'], 'speaker': result['speaker'],
                   'labeled': result['labeled'], 'correct': result['correct'], 'wrong': result['wrong']}
        payload.append(content)
    return jsonify(payload)


@app.route("/getTenNonLabeledTextAudios", methods=['GET'])
@login_required
def getTenNonLabeledTextAudios():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM text_audio where labeled = 0 group by id asc limit 10")
    rv = cur.fetchall()
    payload = []
    for vi in rv:
        content = {'id': vi['id'], 'audioStart': vi['audioStart'], 'audioEnd': vi['audioEnd'], 'text': vi['text'],
                   'fileId': vi['fileId'], 'speaker': vi['speaker'], 'labeled': vi['labeled'], 'correct': vi['correct'],
                   'wrong': vi['wrong']}
        payload.append(content)
    return jsonify(payload)


@app.route("/getTopFive", methods=['GET'])
@login_required
def getTopFive():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT user.id, user.username, COUNT(user_and_text_audio.user_id) FROM user_and_text_audio JOIN user ON user.id = user_and_text_audio.user_id GROUP BY user.id LIMIT 5")
    rv = cur.fetchall()
    payload = []
    for result in rv:
        content = {'id': result['id'], 'username': result['username'],
                   'count': result['COUNT(userAndTextAudio.userId)']}
        payload.append(content)

    return jsonify(payload)


@app.route("/getLabeledSums", methods=['GET'])
@login_required
def getLabeledSums():
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(id) FROM text_audio WHERE correct != 0")
    correct = cur.fetchone()
    cur.execute("SELECT COUNT(id) FROM text_audio WHERE wrong != 0")
    wrong = cur.fetchone()
    cur.execute("SELECT COUNT(id) FROM text_audio")
    total = cur.fetchone()
    return jsonify({'correct': correct['COUNT(id)'], 'wrong': wrong['COUNT(id)'], 'total': total['COUNT(id)']})


# TODO update method to reflect new architecture
@app.route("/getRecordingDataById", methods=['GET'])
@login_required
def getRecordingDataById():
    cur = mysql.connection.cursor()
    cur.execute("SELECT id,  user_id FROM recording WHERE id = %s",
                [request.args.get('id')])
    recording = cur.fetchone()
    return jsonify({'id': recording['id'], 'text': 'TODO remove or replace', 'userId': recording['userId']})


# TODO update method to reflect new architecture
@app.route("/getAllRecordingData", methods=['GET'])
@login_required
def getAllRecordingData():
    cur = mysql.connection.cursor()
    cur.execute(
        "SELECT recording.id,  user.username, recording.time FROM recording JOIN user on user.id = recording.user_id", )
    recording = cur.fetchall()
    payload = []
    for record in recording:
        payload.append(record)
    return jsonify(payload)


@app.route("/getRecordingAudioById", methods=['GET'])
@login_required
def getRecordingAudioById():
    cur = mysql.connection.cursor()
    cur.execute("SELECT audio FROM recording WHERE id = %s",
                [request.args.get('id')])
    audio = cur.fetchone()
    return Response(audio['audio'], mimetype='audio/ogg')


@app.route("/getAudio", methods=['GET'])
@login_required
def getAudio():
    return send_from_directory(os.path.join(baseDir, request.args.get('id')), 'audio.wav')


@loginManager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM user WHERE id = %s", user_id)
    usr = cur.fetchone()
    if usr is not None:
        usr = User(usr['id'], usr['email'], usr['password'])
    return usr


if __name__ == '__main__':
    app.run(port=5000)
