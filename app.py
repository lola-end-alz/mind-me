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


def _get_echo_response(speech_output, card_output, reprompt_message, end_session=True):
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
            'shouldEndSession': end_session
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
        toggle, item, question = _parse_request(data['request'])

        if question:
            saved_toggle = db.get_item(item)
            if not saved_toggle:
                saved_toggle = 'off'
            speech_output = '{} is {}'.format(item, saved_toggle)
            card_output = 'user asked if {} is {}. we responded with {}'.format(item, saved_toggle, speech_output)
        else:
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

    # handle LaunchRequest
    intent = request.get('intent', {})
    intent_name = intent.get('name')
    if intent_name in ('ItemToggle', 'ItemToggleQuestion'):
        question = False
        if intent_name == 'ItemToggleQuestion':
            question = True
        return _get_item_toggle_response(intent), question
    else:
        raise Exception('no intent provided or unknown intent name')


def _get_launch_response(intent):
    speech_output = 'welcome to minder! what can i do for you?'
    card_output = 'user launched minder'
    reprompt_message = 'reprompt message. how does this work?'
    should_end_session = False

    return speech_output, card_output, reprompt_message, should_end_session


def _get_item_toggle_response(intent, question=False):
    slots = intent['slots']
    return slots['toggle']['value'], slots['item']['value']


def _get_item_toggle_question_response(intent):
    return


@app.route('/test_sms/<number>/<message>')
def send_message(number, message):
    send_sms('+1 {}'.format(number), message)
    return 'success'

if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True)
