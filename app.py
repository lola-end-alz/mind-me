import logging
from flask import Flask, jsonify, request

from config import Config
from log import configure

configure(Config.ENV)
app = Flask('minder')
logger = logging.getLogger('minder')


@app.before_request
def log_request():
    logger.info('{} {}'.format(request.method, request.path))


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
    logger.info(request.data)
    return jsonify(DEFAULT_ECHO_RESPONSE)


if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True)
