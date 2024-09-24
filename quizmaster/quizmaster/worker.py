'''
Created on 5 janv. 2023

@author: denis
'''
import logging, threading
#from asgiref.sync import sync_to_async
#from django.utils.timezone import make_aware
#from django.conf import settings
from django.db.models import Max, Min
from contrib import utils
from contrib.mqttc import MqttBase
from .models import Session, Queries, Reply, NO_ANSWER, Ranking
from users.models import User


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class QueriesPlayer(threading.Thread):

    def __init__(self, parent, session, row=1, timeout=10, play=True, expected=False, pause=False):
        super().__init__(daemon=True)
        self.parent = parent
        self.session = session
        self.row = row
        self.sleep = timeout
        self.play = play
        self.expected = expected
        self.pause = pause
        self.stop_player = threading.Event()
        self.expected_timer = threading.Event()
        self.quiz_timer = None
        self.queries = None
        self.queryset = None


    def set_queries_iterator(self, row):
        q = Queries.objects.filter(quiz_id=self.session.quiz_id, range__gte=self.row).all()
        self.queries = q.iterator()


    def display_expected(self, delay=5):
        self.expected_timer = threading.Event()

        self.parent.publish_message('cmde', response=True, expected=self.queryset.query.expected)
        self.expected_timer.wait(delay)
        self.parent.publish_message('cmde', response=False)


    def wait_for_new_question(self, sleep):
        self.quiz_timer = threading.Event()

        while sleep >= 0 and not self.quiz_timer.is_set():
            if not self.pause:
                self.parent.publish_message('cmde', countdown=sleep)
                sleep -= 1
            threading.Event().wait(1)

        if not self.expected:
            self.display_expected()


    def run(self):
        logger.info(f'Starting run session {self.session.id}:{self.session.quiz.title}')
        self.set_queries_iterator(self.row)
        self.parent.gamer_prepare_replies(self.session)

        while not self.stop_player.is_set():
            try:
                if self.play:
                    self.queryset = next(self.queries)
                    self.parent.publish_message(
                        'query',
                        qid=self.queryset.id,
                        range=self.queryset.range,
                        timeout=self.sleep,
                        state=self.session.status,
                        **self.queryset.query.details()
                    )
                    self.wait_for_new_question(self.sleep)
                else:
                    threading.Event().wait(1)

            except StopIteration:
                self.session.status = Session.ENDED
                self.session.save()
                break
            except Exception as e:
                logger.error(f'run error {e}')

        logger.info(f'End of quiz process')
        self.parent.player = None
        # send results
        self.parent.gamer_send_result_replies(self.session)
        self.parent.publish_message('qz-stopped', sid=self.session.id)


    def stop_timers(self):
        self.quiz_timer.set()
        self.expected_timer.set()

    def stop(self):
        self.stop_timers()
        if not self.stop_player.is_set():
            self.stop_player.set()


class Topics:

    def __init__(self, topics):
        from .settings import TOPIC_KEYS
        self.topic_keys = TOPIC_KEYS
        self.topics = topics.split('/') or None

    def is_values(self):
        return self.topics is not None

    def val(self, k):
        return self.topics[self.topic_keys.get(k)]


class QuizmasterWorker(MqttBase):
    def __init__(self, **p):
        super().__init__(**p)
        self.mediadir = p.get('mediadir')
        self.uuid  = p.get('uuid')
        self.player = None

    def init(self):
        pass

    ## gamer
    #
    def gamer_set_connected(self, uuid):
        #logger.info(f" gamer {uuid} logged in")
        User.objects.filter(uuid__exact=uuid).update(connected=True)


    def gamer_query_connected(self):
        return User.objects.filter(role__in=[User.GAMER, User.TESTER], connected=True)


    def gamer_connected(self):
        return self.gamer_query_connected().all()


    def gamer_connected_id(self):
        return [ u.id for u in  self.gamer_connected()]


    def gamer_unconnect_all(self):
        User.objects.filter(role__in=[User.GAMER, User.TESTER]).update(connected=False)
        #logger.info(f"Logout all players and relaod their page")
        self.publish_message('qz-reload')


    def gamer_connected_list(self):
        d = {}
        for u in  self.gamer_connected():
            d.update({ u.uuid: {'gamer': u.username, 'color': u.color} })
        return d


    def gamer_create_reply(self, session_id, userid, row):
        Reply.objects.create(
            session_id=session_id,
            user_id=userid,
            range=row,
            response=NO_ANSWER,
            result=False
        )


    def gamer_update_reply(self, userid, row, response, result):
        Reply.objects.filter(session_id=self.player.session.id, user_id=userid, range=row).update(
            response=response,
            result=result
        )


    def gamer_prepare_replies(self, session):
        rows = Queries.objects.filter(quiz_id=session.quiz_id).values_list('range', flat=True).distinct()
        for u in self.gamer_connected():
            for row in rows:
                self.gamer_create_reply(session.id, u.id, row)


    def gamer_prepare_ranking(self, session, user, correct, wrong, missing):
        Ranking.objects.create(session_id=session.id, user_id=user.id, correct=correct, wrong=wrong, missing=missing)


    def gamer_update_ranking(self, session_id):
        max_value = Ranking.objects.aggregate(maxi=Max('correct'))['maxi']
        min_value = Ranking.objects.aggregate(mini=Min('correct'))['mini']
        rank = 1
        for v in range(max_value, min_value-1, -1):
            if Ranking.objects.filter(session_id=session_id, correct__exact=v).update(rank=rank) !=0 :
                rank+=1
        for r in Ranking.objects.filter(session_id=session_id).order_by('rank').all():
            self.publish_message('rank', uuid=r.user.uuid, rank=r.rank)


    def gamer_send_result_replies(self, session):
        gamers = self.gamer_connected()
        for u in gamers.all():
            reply = Reply.objects.filter(session_id=session.id, user_id=u.id)
            wrong = reply.filter(result__exact=0).count()
            correct = reply.filter(result__exact=1).count()
            missing = reply.filter(response=99).count()

            self.gamer_prepare_ranking(session, u, correct, wrong, missing)
            self.publish_message('results', uuid=u.uuid, correct=correct, wrong=wrong, missing=missing)


    ## mqtt publishing
    #
    def publish_message(self, evt, **payload):
        self._publish_message(f'{self.topic_base}/{utils.ts_now()}/{evt}', **payload)


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
        self.publish_message('status', alive=False)
        logger.info(f'WAITING 1s for last message')
        threading.Event().wait(1)


    def _on_connect_info(self, info):
        logger.info(f"{info}\n    subs: {self.subscriptions}\n")
        self.init()
        self.publish_message('status', alive=True)


    def web_query(self, evt, payload):
        if evt=='quizstart':
            if not self.player:
                session = Session.objects.get(pk=payload.get('sid'))

                session.registered = self.gamer_query_connected().count()
                session.rownumber = int(payload.get('q_rows'))
                session.save()

                self.player = QueriesPlayer(self,
                    session,
                    row=payload.get('range'),
                    timeout=payload.get('timeout'),
                    expected=payload.get('expected'),
                )
                self.player.start()

                self.publish_message(
                    'qz-started',
                    sid=self.player.session.id,
                    date=int(self.player.session.date.timestamp())*1000,
                    title=self.player.session.quiz.title,
                    gamers=self.gamer_connected_list(),
                    q_rows=session.rownumber,
                    registered=session.registered,
                )

        elif evt=='onopen':
            self.publish_message('status', alive=True, gamers=self.gamer_connected_list())

        elif evt=='quizpause':
            if self.player:
                self.player.session.status = Session.PAUSED
                self.player.session.save()
                self.player.play = not self.player.play
                self.publish_message('qz-paused') if not self.player.play else self.publish_message('qz-restarted')

        elif evt=='quizstop':
            if self.player:
                self.player.session.status = Session.STOPPED
                self.player.session.save()
                self.player.stop()

        elif evt=='quiztimeout':
            sleep = payload.get('timeout')
            if self.player and sleep:
                self.player.sleep = int(sleep)

        elif evt=='quizrange':
            row=payload.get('range')
            if self.player and row:
                self.player.set_queries_iterator(int(row))

        elif evt=='quizexpected':
            expected = payload.get('expected')
            if self.player:
                self.player.expected = expected

        elif evt=='ranking':
            self.gamer_update_ranking(payload.get('sid'))

        elif evt=='unconnect':
            self.gamer_unconnect_all()


    def dev_query(self, evt, uuid, payload):
        if evt=='onopen':
            self.gamer_set_connected(uuid)
            if self.player:
                self.publish_message(
                    'qz-reinit',
                    sid=self.player.session.id,
                    date=int(self.player.session.date.timestamp())*1000,
                    title=self.player.session.quiz.title,
                    range=self.player.queryset.range, timeout=self.player.sleep, **self.player.queryset.query.details(),
                )
            else:
                self.publish_message('status', alive=True)

        elif evt in ['onstatus', 'ping']:
            self.gamer_set_connected(uuid)

        elif evt == 'reply':
            if self.player:
                userid = payload.get('userid')
                qid = payload.get('qid')
                response = int(payload.get('value'))
                try:
                    q = Queries.objects.get(id=qid)
                    self.gamer_update_reply(userid, q.range, response, response==q.query.expected)
                except:
                    pass


    def _on_message_callback(self, topic, payload):
        try:
            #logger.info(f"on_message_callback >> {topic} {payload}" )
            topics = Topics(topic)
            dev, evt, uuid = topics.val('dev'), topics.val('evt'), topics.val('uuid')

            if evt=='onclose':
                self.publish_message('status', alive=True)

            elif dev == 'web':
                self.web_query(evt, payload)

            elif dev == "box":
                self.dev_query(evt, uuid, payload)

        except Exception as e:
            logger.error(f'on message callback error {e}')


    async def mqtt_start(self):
        self.client.connect_async(self.host, self.port, self.keepalive)
        logger.info("Start mqtt service" )
        self.client.loop_start()

