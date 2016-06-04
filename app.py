
from flask import Flask, jsonify, request

from config import Config
from log import configure


configure(Config.ENV)
app = Flask('mind-me')


@app.route('/')
def index():
    return jsonify(status='ok', data='hello')


@app.route('/', methods=['POST'])
def minder():
    return jsonify(data=request.data)


if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True)
