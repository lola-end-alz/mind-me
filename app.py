from flask import Flask, jsonify, request


app = Flask('mind-me', static_url_path='')


DEFAULT_ECHO_RESPONSE = {
    'version': '1.0',
    'response': {
        'outputSpeech': {
            'type': 'PlainText',
            'text': 'output speech for alexa'
        },
        'card': {
            'type': 'Simple',
            'title': 'HelloMinder',
            'content': 'minder is working?!'
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': 'reprompting the message?'
            }
        },
        'shouldEndSession': False
    },
    'sessionAttributes': {'source': 'minder'}
}


@app.route('/')
def index():
    return jsonify(status='ok', data='hello')


@app.route('/', methods=['POST'])
def minder():
    return jsonify(DEFAULT_ECHO_RESPONSE)


if __name__ == '__main__':
    app.run(debug=True)
