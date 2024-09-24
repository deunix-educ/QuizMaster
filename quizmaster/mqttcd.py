#!../.venv/bin/python
# encoding: utf-8
#
#
# DD
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quizmaster.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import django
django.setup()

from django.conf import settings
import atexit, logging
from quizmaster.worker import QuizmasterWorker


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    try:
        daemon = QuizmasterWorker(**settings.MQTT_WORKER)
        atexit.register(daemon.stopMQTT)
        daemon.startMQTT()

    except Exception as e:
        logger.error(f'\n    quizmasterWorker error {e}')


if __name__ == '__main__':
    main()



