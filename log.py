import logging.config


def configure(env):

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': True,

        'formatters': {
            'standard': {
                'format': '%(name)s - %(levelname)s - %(message)s'
            },
        },
        'handlers': {
            'default': {
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            'root': {
                'level': 'WARN',
                'handlers': ['default']
            },
            'minder': {
                'level': 'DEBUG' if env in ('dev', 'local', 'test') else 'INFO',
                'handlers': ['default']
            },
            'rq.worker': {
                'level': 'WARN',
                'handlers': ['default']
            }
        }
    })
