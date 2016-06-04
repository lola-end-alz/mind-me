
from db import db
from rq import Worker, Connection

listen = ['default']


if __name__ == '__main__':
    worker = Worker(['default'], connection=db)
    worker.work()
