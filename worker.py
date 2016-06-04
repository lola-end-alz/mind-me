import os
from config import Config
from db import db
from rq import Worker, Queue, Connection

listen = ['default']

if __name__ == '__main__':
    with Connection(db):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
