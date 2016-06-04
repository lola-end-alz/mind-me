from flask import Flask, jsonify, request


app = Flask('mind-me', static_url_path='')


@app.route('/')
def index():
    return jsonify(status='ok', data='hello')


@app.route('/', methods=['POST'])
def minder():
    return jsonify(data=request.data)


if __name__ == '__main__':
    app.run(debug=True)
