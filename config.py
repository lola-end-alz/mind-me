import os


class Config(object):

    PORT = int(os.environ.get('PORT', 7200))
    ENV = os.environ.get('MINDER_ENV', 'dev').lower()
