#
import logging
from django.utils.translation import gettext_lazy as _
from django import forms
#from django.contrib import messages
from .models import Topic, Session, Queries, Quiz, QUIZ_LEVEL
from users.models import User
from contrib.models import DF_FILTERS as date_filters, DF_CHOICES as from_dates

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

level_msg = str(_('All levels'))
quiz_msg = str(_('Choose a quiz'))


def SessionFilterForm(request):
    queryset = Session.objects
    date = request.POST.get('date')
    quizid = request.POST.get('quiz')
    if request.method == "POST":
        if date:
            queryset = date_filters[date](queryset, 'date')
        if quizid:
            queryset = queryset.filter(quiz_id=quizid)

    else:
        queryset = date_filters['week'](queryset, 'date')
    queryset = queryset.all()


    class _SessionFilterForm(forms.Form):
        date  = forms.ChoiceField(
            label=_('From date'),
            choices=from_dates,
            widget=forms.Select(attrs={'class': 'w3-select', 'onchange': 'this.form.submit()'}),
            initial='week',
            required=False,
        )
        quiz = forms.ModelChoiceField(
            queryset=Quiz.objects.filter(active=True).all(),
            label=_("Quiz"),
            widget=forms.Select(attrs={'class': 'w3-select', 'onchange': 'this.form.submit()'}),
            empty_label=f"---- {quiz_msg}",
            required=False,
        )
        session = forms.ModelChoiceField (
            queryset=queryset,
            widget=forms.Select(attrs={'class': 'w3-select', 'onchange': 'this.form.submit()'}),
            label=_('Sessions'),
            empty_label= _('Choose a session'),
            required=False,
        )
    return _SessionFilterForm


def QuizForm(level, submit=False):
    queryset = Quiz.objects.filter(active=True)
    queryset = queryset.all() if level is None else queryset.filter(level__exact=level)

    fn = ';'
    if submit:
        fn = 'this.form.submit()'

    class _QuizForm(forms.Form):
        levels = forms.ChoiceField(
            choices=[ (None, f"---- {level_msg}"), ] + QUIZ_LEVEL,
            widget=forms.Select(attrs={'class': 'w3-select', 'onchange': 'this.form.submit()'}),
            label=_("Level"),
            initial=0,
            required=False
        )
        quiz = forms.ModelChoiceField(
            queryset=queryset,
            label=_("Quiz"),
            widget=forms.Select(attrs={'class': 'w3-select', 'onchange': f'{fn}'}),
            empty_label=f"---- {quiz_msg}",
            required=False,
        )
    return _QuizForm


def quizFilterForm(request, level=None, submit=False):
    try:
        if level is not None:
            level = int(level)
    except:
        level=None
    return QuizForm(level, submit)(data=request.POST or None)


def QueriesForm(quizid):
    queryset =  Queries.objects.filter(quiz_id=quizid).all()

    class _QueriesForm(forms.Form):
        query = forms.ModelChoiceField(
            queryset=queryset,
            label=_("Queries composition"),
            widget=forms.Select(attrs={'class': 'w3-select', }),
            empty_label=None,
            required=False,
        )
    return _QueriesForm


class QuizzesForm(forms.Form):

    topic = forms.ModelChoiceField(
            queryset=Topic.objects.all(),
            label=_("Topic title"),
            widget=forms.Select(attrs={'class': 'w3-select', }),
            empty_label=_("Topic title"),
            required=True,
        )
    level = forms.ChoiceField(
        choices=[ (None, f"---- {level_msg}"), ] + QUIZ_LEVEL,
        widget=forms.Select(attrs={'class': 'w3-select'}),
        label=_("Quiz level"),
        initial=0,
        required=True
    )
    title = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w3-input'}),
        label=_("Quiz title"),
        required=True,
        initial=""
    )


class GamersForm(forms.Form):
    ROLES = [
        (None, "----"),
        (User.GAMER, '%s' % _("Gamer user") ),
        (User.TESTER, '%s' % _("Gamer tester")),
    ]

    YES_NO = [
        (False, _("No") ),
        (True,  _("Yes")),
    ]

    connected = forms.ChoiceField(
        choices=YES_NO,
        widget=forms.Select(attrs={'class': 'w3-select', 'onchange': 'this.form.submit()'}),
        label=_("Connected"),
        initial=True,
    )

    role = forms.ChoiceField(
        choices=ROLES,
        widget=forms.Select(attrs={'class': 'w3-select', 'onchange': 'this.form.submit()'}),
        label=_("Games type"),
        initial=None,
        required=False
    )


