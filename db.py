
from urlparse import urlparse
from redis import Redis
from mockredis import MockRedis
from config import Config

parts = urlparse(Config.REDIS_URL)

import pdb;pdb.set_trace()

if Config.LOCAL:
    db = MockRedis()
else:
    db = Redis(host=parts.hostname,
               port=parts.port)


def set_item(item, toggle):
    db.set(item, toggle)


def get_item(item):
    return db.get(item)
