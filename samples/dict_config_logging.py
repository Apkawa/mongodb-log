import sys
sys.path.append('..')

import logging
from logging.config import dictConfig

LOGGING = {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {
                    'mongodb': {
                    'level':'DEBUG',
                    'class': 'mongolog.handlers.MongoHandler',
                    'db': 'mongolog',
                    'collection': 'log',
                    'host': 'localhost',
                    'port': None,
                    'formatter': 'mongolog',
                },
            },
            'formatters': {
                'mongolog': {
                            '()': 'mongolog.handlers.MongoFormatter',
                            'format': '%(message)s',
                    },
            },

            'loggers': {
                '': {
                    'level': 'DEBUG',
                    'handlers': ['mongodb'],
                    },
            },
        }


dictConfig(LOGGING)

if __name__ == '__main__':

    log = logging.getLogger('example')

    log.debug("1 - debug message")
    log.info("2 - info message", extra={'1':2})
    log.warn("3 - warn message")
    log.error("4 - error message")
    log.critical("5 - critical message")
    try:
        raise Exception("6 - exception message")
    except Exception:
        log.exception("6 - exception message")
