import daemon
import logging
import logging.config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'default': {
            'format': '%(asctime)s %(levelname)s - %(message)s',
            'datefmt': '[%d/%b/%Y %H:%M:%S]'
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/tmp/crawler.log',
            'formatter': 'default'
        },
    },
    'loggers': {
        'daemon': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        }
    }
})

logger = logging.getLogger('daemon')

daemon_context = daemon.DaemonContext(
    files_preserve=[logger.handlers[0].stream],
)
