
from twilio.rest import TwilioRestClient
from config import Config


def send_sms(number, message):
    client = TwilioRestClient(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
    client.messages.create(
        to=number,
        from_=Config.TWILIO_FROM_NUMBER,
        body=message
    )