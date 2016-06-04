import logging
from datetime import datetime, timedelta
from rq_scheduler import Scheduler
from config import Config
from sms import send_sms
from db import set_item, get_item


scheduler = Scheduler(connection=db)
logger = logging.getLogger('minder.job')


def schedule_the_job(item):
    the_job = scheduler.enqueue_in(timedelta(seconds=3),
                                   send_sms,
                                   Config.USER_PHONE_NUMBER,
                                   'Did you remember to turn off the {}'.format(item))
    set_item('the_job', the_job.id)


def cancel_the_job():
    the_job = get_item('the_job')
    if the_job in scheduler:
        scheduler.cancel(the_job)
