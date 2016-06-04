
from urlparse import urlparse
from redis import Redis

from config import Config

parts = urlparse(Config.REDIS_URL)
db = Redis(host=parts.hostname,
           port=parts.port)


def set_item(item, toggle):
    db.set(item, toggle)


def get_item(item):
    return db.get(item)
