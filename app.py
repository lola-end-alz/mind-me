import logging
import json
from flask import Flask, jsonify, request

from config import Config
from log import configure
from sms import send_sms
from db import db


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


@app.route('/', methods=['POST'])
def minder():
    data = json.loads(request.data)
    logger.info(data)

    try:
        toggle, item = _parse_request(data['request'])
        speech_output = 'you\'ve turned {} the {}'.format(toggle, item)
        card_output = 'user turned {} the {}'.format(toggle, item)
        reprompt_message = 'reprompt message. how does this work?'

        db.set_item(item, toggle)
        send_sms(Config.USER_PHONE_NUMBER, card_output)
        response = _get_echo_response(speech_output, card_output, reprompt_message)
    except Exception:
        speech_output = 'sorry, i didn\'t understand that. please try again'
        card_output = 'couldn\'t understand command from user'
        reprompt_message = 'reprompt message. how does this work?'
        response = _get_echo_response(speech_output, card_output, reprompt_message)
    return jsonify(response)


def _parse_request(request):
    request_type = request['type']
    if request_type != 'IntentRequest':
        raise Exception()

    intent = request.get('intent', {})
    if intent.get('name') != 'ItemToggle':
        raise Exception('no intent provided or unknown intent name')

    slots = intent['slots']
    return slots['toggle']['value'], slots['item']['value']


if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True)
