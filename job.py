import logging

logger = logging.getLogger('minder.job')

def dummy_job():
    logger.info('Running fake job')
    sleep(10)

