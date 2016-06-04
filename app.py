from flask import Flask, jsonify


app = Flask('mind-me', static_url_path='')


@app.route('/')
def index():
    return jsonify(status='ok', data='hello')


if __name__ == '__main__':
    app.run(debug=True)
