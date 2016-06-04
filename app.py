import logging
import json
from flask import Flask, jsonify, request

from config import Config
from log import configure

configure(Config.ENV)
app = Flask('minder')
logger = logging.getLogger('minder')


@app.before_request
def log_request():
    logger.info('{} {}'.format(request.method, request.path))


def _get_echo_response(speech_output, card_output, reprompt_message):
    return {
        'version': '1.0',
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': speech_output
            },
            'card': {
                'type': 'Simple',
                'title': 'Minder',
                'content': card_output
            },
            'reprompt': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': reprompt_message
                }
            },
            'shouldEndSession': False
        },
        'sessionAttributes': {'source': 'minder'}
    }


@app.route('/')
def index():
    return jsonify(status='ok', data='hello')

@app.route('/oauth2_callback')
def oauth_redirect():
	content = response.content
	import pdb; pdb.set_trace()
	return jsonify(status='ok', response=response.content)

@app.route('/', methods=['POST'])
def minder():
    data = json.loads(request.data)
    logger.info(data)

    response = _parse_request(data['request'])
    return jsonify(response)


def _parse_request(request):
    request_type = request['type']
    if request_type != 'IntentRequest':
        raise Exception()

    intent = request['intent']
    if intent['name'] != 'ItemToggle':
        raise Exception('unknown intent name')

    slots = intent['slots']
    item = slots['item']['value']
    toggle = slots['toggle']['value']

    speech_output = 'you\'ve turned {} the {}'.format(toggle, item)
    card_output = 'user turned {} the {}'.format(toggle, item)
    reprompt_message = 'reprompt message. how does this work?'

    return _get_echo_response(speech_output, card_output, reprompt_message)

@app.route('/oauth2_callback')
def oauth_redirect():
	content = response.content
	import pdb; pdb.set_trace()
	return jsonify(status='ok', response=response.content)

@app.route('/calendar')
def authenticate():
	from calendar.oauth2 import connect_calendar
	connect_calendar()

if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True)
