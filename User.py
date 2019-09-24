import mysql.connector
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask import Flask, request, jsonify


class User:
    def __init__(self, id, firstName, lastName, email, username, avatarVersion):
        self.id = id
        self.firstName = firstName
        self.lastName = lastName
        self.email = email
        self.username = username
        self.avatarVersion = avatarVersion

    def is_authenticated(app: Flask(__name__), bcrypt: Bcrypt, username: str, password: str) -> bool:
        CORS(app)
        dataBase = mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='password',
            database='labeling-tool'
        )
        cursor = dataBase.cursor()
        cursor.execute("SELECT * FROM user WHERE username = %s", (username,))
        rv = cursor.fetchall()
        for res in rv:
            return bcrypt.check_password_hash(res[6], password)
