import logging
from flask import Flask, jsonify, request

from config import Config
from log import configure

configure(Config.ENV)
app = Flask('minder')
logger = logging.getLogger('minder')


DEFAULT_ECHO_RESPONSE = {
    'version': '1.0',
    'response': {
        'outputSpeech': {
            'type': 'PlainText',
            'text': '{speech_output}'
        },
        'card': {
            'type': 'Simple',
            'title': 'Minder',
            'content': '{card_output}'
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': '{reprompt_message}'
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
    data = request.data
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
    toggle = slots['toggle']['on']

    speech_output = 'you\'ve turned {} the {}'.format(toggle, item)
    card_output = 'user turned {} the {}'.format(toggle, item)
    reprompt_message = 'reprompt message. how does this work?'

    return DEFAULT_ECHO_RESPONSE.format(speech_output=speech_output,
                                        card_output=card_output,
                                        reprompt_message=reprompt_message)


if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True)
