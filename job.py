import logging
from datetime import datetime, timedelta
from rq_scheduler import Scheduler
from config import Config
from sms import send_sms
from db import db, set_item, get_item


scheduler = Scheduler(connection=db)
logger = logging.getLogger('minder.job')


def schedule_the_job(item):
    logger.info('Aquiring lock before scheduling')
    with db.lock('the_job_lock'):
        scheduled = scheduler.enqueue_in(timedelta(seconds=Config.REMINDER_DELAY),
                                         the_job,
                                         item)
        set_item('the_job', scheduled.id)
    logger.info('Released lock after scheduling')


def the_job(item):
    logger.info('Running job')
    send_sms(Config.PROVIDER_PHONE_NUMBER, 'Did you remember to turn off the {}'.format(item))
    logger.info('Sent sms')
    schedule_the_job(item)
    logger.info('Scheduled job to run again')


def cancel_the_job():
    with db.lock('the_job_lock'):
        scheduled = get_item('the_job')
        logger.info('Trying to cancel job {}'.format(scheduled))
        logger.info('All jobs {}'.format(scheduler.get_jobs()))
        if scheduled in scheduler:
            logger.info('Calling scheduler.cancel()')
            scheduler.cancel(scheduled)
        else:
            logger.info('Unable to find job to cancel')
    logger.info('Released lock after cancelling')
