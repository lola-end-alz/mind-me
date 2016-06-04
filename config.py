import os


class Config(object):

    LOCAL = True if os.environ.get('LOCAL') is not None else False
    PORT = int(os.environ.get('PORT', 7200))
    ENV = os.environ.get('MINDER_ENV', 'dev').lower()
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_FROM_NUMBER = os.environ.get('TWILIO_FROM_NUMBER')

    USER_PHONE_NUMBER = os.environ.get('USER_PHONE_NUMBER')
    PROVIDER_PHONE_NUMBER = os.environ.get('PROVIDER_PHONE_NUMBER')
    REMINDER_DELAY = os.environ.get('REMINDER_DELAY', 5)
    WORKER_TTL = os.environ.get('WORKER_TTL', 5000)
