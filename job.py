import logging
from rq_scheduler import Scheduler
from db import db


scheduler = Scheduler(connection=db)
logger = logging.getLogger('minder.job')


def dummy_job():
    logger.info('Running fake job')
    sleep(10)

