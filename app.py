import logging
import json
import flask
import uuid
import httplib2
from datetime import datetime, timedelta
from flask import Flask, jsonify, request

from config import Config
from log import configure
from sms import send_sms
from db import set_item, get_item, db

from rq import Queue
from job import schedule_the_job, cancel_the_job

from apiclient import discovery
from oauth2client import client


configure(Config.ENV)
app = Flask('minder')
app.secret_key = str(uuid.uuid4())
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
        launch, toggle, item, question = _parse_request(data['request'])
        if launch:
            speech_output = 'welcome to minder! what can i do for you today?'
            card_output = 'user launched minder'
            reprompt_message = 'what can i do for you today?'
            response = _get_echo_response(speech_output, card_output, reprompt_message, end_session=False)
        else:
            if question:
                saved_toggle = get_item(item)
                if not saved_toggle:
                    saved_toggle = 'off'
                speech_output = 'hello, the {} is {}'.format(item, saved_toggle)
                card_output = 'user asked if {} is {}. we responded with {}'.format(item, saved_toggle, speech_output)
                reprompt_message = ''
            else:
                speech_output = 'you\'ve turned {} the {}'.format(toggle, item)
                card_output = 'user turned {} the {}'.format(toggle, item)
                reprompt_message = ''

                if toggle == 'on':
                    schedule_the_job(item)

                if toggle == 'off':
                    logger.info('Attempting to cancel job')
                    cancel_the_job()

                set_item(item, toggle)
                send_sms(Config.USER_PHONE_NUMBER, card_output)

            response = _get_echo_response(speech_output, card_output, reprompt_message)
    except Exception as e:
        logger.error(e)
        speech_output = 'sorry, i didn\'t understand that. please try again'
        card_output = 'couldn\'t understand command from user'
        reprompt_message = 'reprompt message. how does this work?'
        response = _get_echo_response(speech_output, card_output, reprompt_message)

    return jsonify(response)


def _parse_request(request):
    request_type = request['type']
    if request_type not in ('IntentRequest', 'LaunchRequest'):
        raise Exception('unrecognized request type')

    if request_type == 'LaunchRequest':
        return True, None, None, False
    else:
        intent = request.get('intent', {})
        intent_name = intent.get('name')
        if intent_name in ('ItemToggle', 'ItemToggleQuestion'):
            question = False
            if intent_name == 'ItemToggleQuestion':
                question = True
            slots = intent['slots']
            return False, slots['toggle']['value'], slots['item']['value'], question
        else:
            raise Exception('no intent provided or unknown intent name')


# def _get_launch_response(intent):
#     speech_output = 'welcome to minder! what can i do for you?'
#     card_output = 'user launched minder'
#     reprompt_message = 'reprompt message. how does this work?'
#     should_end_session = False

#     return speech_output, card_output, reprompt_message, should_end_session


# def _get_item_toggle_response(intent, question=False):
#     slots = intent['slots']
#     return slots['toggle']['value'], slots['item']['value']


@app.route('/test_sms/<number>/<message>')
def send_message(number, message):
    send_sms('+1 {}'.format(number), message)
    return 'success'


@app.route('/oauth2_callback')
def oauth2_callback():
    flow = client.flow_from_clientsecrets(
        'client_secret.json',
        scope='https://www.googleapis.com/auth/calendar',
        redirect_uri=flask.url_for('oauth2_callback', _external=True))

    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        set_item('credentials', credentials.to_json())
        return flask.redirect(flask.url_for('calendar'))


@app.route('/calendar')
def calendar():
    credentials = get_item('credentials')
    if not credentials:
        return flask.redirect(flask.url_for('oauth2_callback'))

    credentials = client.OAuth2Credentials.from_json(credentials)

    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2_callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        calendar_service = discovery.build('calendar', 'v3', http_auth)
        response = calendar_service.events().list(calendarId='primary').execute()

        return jsonify(status='ok', events=response.get('items'))


@app.route('/calendar/create')
def create_event():
    credentials = client.OAuth2Credentials.from_json(get_item('credentials'))
    http_auth = credentials.authorize(httplib2.Http())
    calendar_service = discovery.build('calendar', 'v3', http_auth)
    start = datetime.utcnow() + timedelta(minutes=5)
    end = start + timedelta(minutes=5)
    response = calendar_service.events().insert(
        calendarId='primary',
        body={
            'description': 'testing',
            'start': {'dateTime': start.isoformat() + 'Z'},
            'end': {'dateTime': end.isoformat() + 'Z'}
        }
    ).execute()
    return jsonify(status='ok', events=response.get('items'))


if __name__ == '__main__':
    app.run(port=Config.PORT, debug=True)
