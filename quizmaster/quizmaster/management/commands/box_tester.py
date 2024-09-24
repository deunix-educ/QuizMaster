#
# encoding: utf-8
#import sys
#import os, pathlib
from django.conf import settings
from django.core.management import BaseCommand
from django.utils.translation import gettext_lazy as _

from multiprocessing import Process
import threading, logging
from contrib import utils
from contrib.mqttc import MqttBase
from quizmaster.worker import Topics
from users.models import User, new_user


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ClientBoxWorker(MqttBase):

    def __init__(self, user):
        if not user:
            raise Exception(_('ClientBoxWorker: user not a gamer tester'))
        self.user = user
        config = dict(
            user=user,
            topic_base=f'{settings.BASE_ORIGINE}/box/{user.uuid}',
            topic_subs=[
                [f'{settings.BASE_ORIGINE}/srv/{utils.get_uuid()}/#', 0],
                [f'{settings.BASE_ORIGINE}/web/{utils.get_uuid()}/#', 0],
            ],
            **settings.CLIENT_BOX
        )
        super().__init__(**config)


    ## mqtt publishing
    #
    def publish_message(self, evt, **payload):
        self._publish_message(f'{self.topic_base}/{utils.ts_now()}/{evt}', **payload)


    def reply(self, qid, boolean, timeout):
        v = utils.randint(stop=1) if boolean else utils.randint(start=2, stop=5)
        print(f"Reply {self.user.username} >> qid={qid}, boolean={boolean}, timeout={timeout}, value={v}")

        threading.Event().wait(utils.randint(start=1, stop=timeout-1))
        self.publish_message('reply', userid=self.user.id, qid=qid, value=v)


    ## mqtt events
    #
    def _on_log(self, mqttc, obj, level, string):  # @UnusedVariable
        try:
            if 'PINGRESP' in string:
                #logger.info(f"_on_log {string}")
                self.publish_message('status', alive=True)
        except Exception as e:
            logger.error(f"_on_log error {e}")


    def _on_stop_mqtt(self):
        self.publish_message('onclose', gamer=self.user.username)
        logger.info(f'WAITING 1s for last message')
        threading.Event().wait(1)


    def _on_connect_info(self, info):
        logger.info(f"{info}\n    subs: {self.subscriptions}\n    gamer: {self.user.username}")
        self.publish_message('onopen', gamer=self.user.username)


    def _on_message_callback(self, topic, payload):
        try:
            #print("on_message_callback.............", topic)
            topics = Topics(topic)
            evt = topics.val('evt')

            if evt=='status':
                self.publish_message('onstatus', gamer=self.user.username)

            elif evt=='query':
                self.reply(payload.get('qid'), payload.get('boolean'), payload.get('timeout'))

        except Exception as e:
            logger.error(f'on message callback error {e}')


def main_process(user):
    try:
        daemon = ClientBoxWorker(user)
        daemon.startMQTT()
    except Exception as e:
        logger.error(f'\n    ClientBoxWorker error {e}')
    finally:
        daemon.stopMQTT()


def gamers(amount):
    User.objects.filter(role__exact=User.TESTER).update(connected=False)
    users = []
    n = 0
    for user in User.objects.filter(role__exact=User.TESTER).all():
        users.append(user)
        n+=1
        if n >= amount:
            break
    while n < amount:
        users.append(new_user(role=User.TESTER))
        n+=1
    return users


class Command(BaseCommand):

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument("--amount", default=1, help=f"Gamers amount")


    def handle(self, *args, **option):
        amount = int(option.get('amount'))
        procs = []

        for gamer in gamers(amount):
            proc = Process(target=main_process, args=(gamer,))
            procs.append(proc)
            proc.start()

        while True:
            try:
                threading.Event().wait(1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f'ClientBoxWorker processes error {e}')
            finally:
                for proc in procs:
                    proc.join()

