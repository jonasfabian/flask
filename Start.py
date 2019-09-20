import mysql.connector
from flask import Flask, jsonify
from flask_cors import CORS
from flask_restful import Api

app = Flask(__name__)
api = Api(app)
CORS(app)
dataBase = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='password',
    database='labeling-tool'
)


@app.route("/")
def hello():
    mycursor = dataBase.cursor()
    mycursor.execute("SELECT * FROM user")
    myresult = mycursor.fetchall()
    return jsonify(myresult)


if __name__ == '__main__':
    app.run(port=5002)
