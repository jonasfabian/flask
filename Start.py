import mysql.connector
from flask import Flask, jsonify, request
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


@app.route("/getUsers", methods=['GET'])
def getUserById():
    cursor = dataBase.cursor()
    cursor.execute("SELECT * FROM user WHERE id = %s", (request.args.get('id'),))
    return jsonify(cursor.fetchone())


if __name__ == '__main__':
    app.run(port=8080)
