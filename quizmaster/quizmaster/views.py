#
# encoding: utf-8
#from datetime import datetime, timedelta
#from dateutil.parser import parse as parse_date
#from django.contrib.auth.mixins import LoginRequiredMixin
#from django.utils import timezone
#
#from django.utils.translation import gettext_lazy as _
import logging, json, requests
import urllib.parse

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.http import JsonResponse
import paho.mqtt.publish as publish

from users.decorators import login_required, gamer_required, contributor_required, anonymous_required
from users.models import User, new_user
from contrib import utils, ziputil

from . import forms
from . import models
from .  import resources
from .import_export import Import

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def publish_message(evt, **payload):
    publish.single(
        f'{settings.SERVER_TOPIC_BASE}/{utils.ts_now()}/{evt}',
        json.dumps(payload),
        **settings.MQTT_SINGLE
    )

def supervisor_ctl(**kwargs):
    params = urllib.parse.urlencode(kwargs, doseq=True)
    url = f'http://{settings.SUPERVISOR_USERNAME}:{settings.SUPERVISOR_PASSWORD}@{settings.SUPERVISOR_HOSTNAME}:{settings.SUPERVISOR_HOSTPORT}?{params}'
    requests.get(url=url)


@login_required
@anonymous_required
def main(request):
    if not request.user.is_anonymous:
        if request.user.role >= User.CONTRIBUTOR:
            return redirect('home')
    return render(request, 'index.html')

@login_required
@anonymous_required
def login_to_box(request):
    try:
        if not request.user.is_anonymous:
            if request.user.role in [ User.GAMER, User.TESTER ]:
                return redirect('box')
        user = new_user()
        if user:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            return redirect('box')
    except Exception as e:
        logger.error(f'Login to box error {e}')
    return redirect('main')


@login_required
@gamer_required
def gamer_list(request):
    queryset = User.objects.filter(role__in=[User.GAMER, User.TESTER], connected=True)
    if request.method == "POST":
        role = request.POST.get('role')
        connected = request.POST.get('connected')
        if role:
            queryset = User.objects.filter(role__exact=role, connected=connected)
    context = dict(
        form=forms.GamersForm(data=request.POST or None),
        gamers=queryset,
    )
    return render(request, 'gamer_list.html', context)


@login_required
@gamer_required
def quiz_help(request):
    return render(request, 'quiz-help.html')

@login_required
@contributor_required
def quiz_result(request):
    session = None
    ranking = None
    if request.method == "POST":
        sid = request.POST.get('session')
        if sid:
            session = models.Session.objects.get(pk=sid)
            ranking = models.Ranking.objects.filter(session_id=session.id).order_by('rank', 'user')
    context = dict(
        session=session,
        ranking=ranking,
        filter=forms.SessionFilterForm(request)(data=request.POST or None),
    )
    return render(request, 'quiz_result.html', context)



@login_required
@contributor_required
def home(request):
    return render(request, 'home.html')


@login_required
@contributor_required
def quiz(request):
    session = None
    queries = None
    q_rows = None
    if request.method == "POST":
        if request.POST.get('_new'):
            quizid = request.POST.get('quiz')
            if quizid:
                session = models.Session.objects.create(quiz_id=quizid, owner_id=request.user.id)
                queries = models.Queries.objects.filter(quiz_id=quizid)
                q_rows = queries.count()
    context = dict(
        topicbase=settings.CLIENT_TOPIC_BASE,
        topicsubs=json.dumps(settings.CLIENT_TOPIC_SUBS),
        uuid=utils.get_uuid(),
        filter=forms.quizFilterForm(request),
        session=session,
        queries=queries,
        q_rows=q_rows,
        choices=models.Query.choices(),
        **settings.MQTT_CLIENT
    )
    return render(request, 'quiz.html', context)


@login_required
@gamer_required
def box(request):
    context = dict(
        topicbase=f'{settings.BASE_ORIGINE}/box/{request.user.uuid}',
        topicsubs=json.dumps([
            [f'{settings.BASE_ORIGINE}/srv/{utils.get_uuid()}/#', 0],
            [f'{settings.BASE_ORIGINE}/web/{utils.get_uuid()}/#', 0],
        ]),
        uuid=request.user.uuid,
        userid=request.user.id,
        gamer=request.user.username,
        choices=models.Query.choices(),
        **settings.MQTT_CLIENT
    )
    return render(request, 'box.html', context)


@login_required
@contributor_required
def quiz_import(request):

    def result_to_quiz_data(result):
        for r in result:
            r['boolean'] = r.get('boolean') == '1'
            if not r['boolean']:
                r['expected'] = 2 + (ord( r.get('expected')) - ord('A'))
        return result

    result = []
    quiz = None
    uploaded_file_url = ""
    form = forms.QuizzesForm(data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            title = request.POST.get('title')
            level = request.POST.get('level')
            topic = request.POST.get('topic')
            uploaded_file_url = request.FILES['file']
            if uploaded_file_url:
                result = result_to_quiz_data(Import.import_from_csv(request, resources.QueryResourceImport, uploaded_file_url))
                if result:
                    quiz = models.Quiz.objects.create(owner_id=request.user.id, title=title, level=level)
                    row = 1
                    for d in result:
                        query = models.Query.objects.create(
                            owner_id=request.user.id,
                            topic_id=topic,
                            level=level,
                            **d
                        )
                        models.Queries.objects.create(range=row, quiz_id=quiz.id, query_id=query.id)
                        row+=1

        except Exception as e:
            logger.error(f'quiz error {e}')

    context = dict(
        uploaded_file_url=uploaded_file_url,
        form=form,
        quiz=quiz,
        result=result,
    )
    return render(request, 'quiz_import.html', context)


@login_required
@contributor_required
def quiz_export(request):
    queries = None
    quiz = None
    level = None
    if request.method == "POST":
        qid = request.POST.get('quiz')
        if qid:
            level = request.POST.get('level')
            quiz = models.Quiz.objects.get(pk=qid)
            if quiz:
                queries = models.Queries.objects.filter(quiz_id=quiz.id)

    context = dict(
        quiz=quiz,
        queries=queries,
        filter=forms.quizFilterForm(request, level=level, submit=True),
    )
    return render(request, 'quiz_export.html', context)


@login_required
@contributor_required
def quiz_result_to_pdf(request, sid=None):
    try:
        if sid:
            session = models.Session.objects.get(pk=sid)
            ranking = models.Ranking.objects.filter(session_id=session.id).order_by('rank', 'user')
            if ranking:
                context = dict(
                    pagesize='A4',
                    request=request,
                    session=session,
                    ranking=ranking,
                    user=request.user,
                )
                return ziputil.Render.render('print/result.html', context, filename='quiz-result')
    except Exception as e:
        logger.error(f'result_to_pdf error: {e}')
    return redirect('quiz_result')


@login_required
@contributor_required
def quiz_session_delete(request, sid=None):
    try:
        if sid:
            models.Session.objects.filter(id=sid).delete()
    except Exception as e:
        logger.error(f'quiz_session_delete error: {e}')

    return redirect('quiz_result')


@login_required
@contributor_required
def quiz_result_export(request, sid, export):
    try:
        filename = 'quiz-result'
        queryset = models.Ranking.objects.filter(session_id=sid).order_by('rank').all()
        if export=='xls':
            return ziputil.Export.export_to_xls(resources.RankingResource, queryset=queryset, filename=filename)

        elif export=='json':
            return ziputil.Export.export_to_json(resources.RankingResource, queryset=queryset, filename=filename)

        return ziputil.Export.export_to_csv(resources.RankingResource, queryset=queryset, filename=filename)

    except Exception as e:
        logger.error(f'quiz_result_export error: {e}')
    return redirect('quiz_result')


@login_required
@contributor_required
def quiz_queries_export(request, qid, export):
    try:
        quiz = models.Quiz.objects.get(pk=qid)
        filename = f'{quiz.code}'
        queryset = models.Queries.objects.filter(quiz_id=quiz.id).order_by('range').all()

        if export=='xls':
            return ziputil.Export.export_to_xls(resources.QueriesResource, queryset=queryset, filename=filename)

        elif export=='json':
            return ziputil.Export.export_to_json(resources.QueriesResource, queryset=queryset, filename=filename)

        return ziputil.Export.export_to_csv(resources.QueriesResource, queryset=queryset, filename=filename)

    except Exception as e:
        logger.error(f'quiz_queries_export error: {e}')
    return redirect('quiz_export')


@login_required
@contributor_required
def tools(request):
    if request.method == "POST":
        try:
            if request.POST.get('ssdel') == 'on':
                sessions = models.Reply.objects.order_by().values_list('session', flat=True).distinct()
                for s in models.Session.objects.filter(active=True).exclude(id__in=sessions).all():
                    models.Session.objects.filter(id=s.id).delete()

            if request.POST.get('tgdel') == 'on':
                User.objects.filter(role_exact=User.TESTER).delete()

            if request.POST.get('lgout') == 'on':
                publish_message('unconnect')

            if request.POST.get('mqtt'):
                service = request.POST.get('mqtt')
                supervisor_ctl(processname=service, action='restart')

        except Exception as e:
            logger.error(f'tools error {e}')
    return render(request, 'tools.html')


@login_required
@gamer_required
def quiz_mqtt_options(request):
    if request.method == "POST":
        return JsonResponse(dict(status=True, mqttuser=settings.MQTT_USERNAME, mqttpass=settings.MQTT_PASSWORD))
    return JsonResponse({'status': False, })


@login_required
@gamer_required
def box_mqtt_options(request):
    if request.method == "POST":
        return JsonResponse(dict(status=True, mqttuser=settings.MQTT_USERNAME, mqttpass=settings.MQTT_PASSWORD))
    return JsonResponse({'status': False, })


