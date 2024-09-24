'''
Created on 4 janv. 2023

@author: denis
'''
#from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db import models
from users.models import User
from django.template.defaultfilters import slugify


QUIZ_LEVEL = [
    (0, _("Beginner")),
    (1, _("Easy")),
    (2, _("Medium")),
    (3, _("Hard")),
    (4, _("Very hard")),
]

NO_ANSWER= 99

class Topic(models.Model):
    title = models.CharField(_("Topic title"), max_length=32, null=True, blank=True)

    class Meta:
        ordering = ['title',]
        verbose_name = _("Quiz topic")
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.title}'


class Query(models.Model):

    VALUE = [
        (0, _("No")),
        (1, _("Yes")),
        (2, _("A")),
        (3, _("B")),
        (4, _("C")),
        (5, _("D")),
        (6, _("E")),
        (7, _("F")),
        (NO_ANSWER, _("No answer")),
    ]
    owner = models.ForeignKey(User, verbose_name=_("Query owner"), on_delete=models.CASCADE, null=True)
    topic = models.ForeignKey(Topic, verbose_name=_("Topic"), on_delete=models.CASCADE, null=True)
    level = models.SmallIntegerField(_("Query level"), choices=QUIZ_LEVEL, null=True, blank=True, default=0)

    description = models.TextField(_("Query description"), null=True, blank=True)
    boolean = models.BooleanField(_("Boolean"), default=False)
    A = models.CharField(_("Choice number A"), max_length=64, null=True, blank=True)
    B = models.CharField(_("Choice number B"), max_length=64, null=True, blank=True)
    C = models.CharField(_("Choice number C"), max_length=64, null=True, blank=True)
    D = models.CharField(_("Choice number D"), max_length=64, null=True, blank=True)
    E = models.CharField(_("Choice number E"), max_length=64, null=True, blank=True)
    F = models.CharField(_("Choice number F"), max_length=64, null=True, blank=True)
    expected = models.SmallIntegerField(_("Expected answer"), choices=VALUE, null=True, blank=True, default=0)


    @classmethod
    def choices(cls):
        c = []
        for _, v in cls.VALUE:
            c.append(v)
        return c


    def details(self):
        return dict(
            queryid=self.id,
            boolean=self.boolean,
            description=self.description,
            A=self.A,
            B=self.B,
            C=self.C,
            D=self.D,
            E=self.E,
            F=self.F,
        )

    class Meta:
        ordering = ['owner__username', 'topic__title', 'level']
        verbose_name = _("Question")
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.topic.title}: {self.description[:64]}'


class Quiz(models.Model):
    owner = models.ForeignKey(User, verbose_name=_("Quiz owner"), on_delete=models.CASCADE, null=True)
    title = models.CharField(_("Quiz title"), max_length=128, null=True, blank=True)
    code  = models.SlugField(_("Slug title"), max_length=48, blank=True, default='')
    level = models.SmallIntegerField(_("Quiz level"), choices=QUIZ_LEVEL, null=True, blank=True, default=0)
    active = models.BooleanField(_("Active quiz"), default=True)

    @property
    def quiz_level(self):
        for k, v in QUIZ_LEVEL:
            if k == self.level:
                return v
        return ""

    class Meta:
        ordering = ['level', 'title', 'owner__username']
        verbose_name = _("Quiz")
        verbose_name_plural = verbose_name

    def save(self, *args, **kwargs):
        if not self.id:
            self.code = slugify(self.title)
        super().save(*args, **kwargs)


    def __str__(self):
        return f'{self.quiz_level} - {self.title} [{self.owner.username}]'


class Queries(models.Model):
    range = models.SmallIntegerField(_("Query range"), null=True, blank=True, default=1)
    quiz = models.ForeignKey(Quiz, verbose_name=_("Quiz"), on_delete=models.CASCADE, null=True)
    query = models.ForeignKey(Query, verbose_name=_("Query"), on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['quiz', 'range']
        unique_together = ('quiz', 'query')
        verbose_name = _("Queries composition")
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.range} - {self.query.description[:32]}'


class Session(models.Model):
    STOPPED = 0
    STARTED = 1
    PAUSED = 2
    ENDED = 3

    STATUS = [
        (STOPPED, _("Session stopped")),
        (STARTED, _("Session started")),
        (PAUSED, _("Session paused")),
        (ENDED, _("Session ended")),
    ]

    date = models.DateTimeField("Date", auto_now_add=True)
    owner = models.ForeignKey(User, verbose_name=_("Session owner"), on_delete=models.CASCADE, null=True)
    quiz = models.ForeignKey(Quiz, verbose_name=_("Quiz"), on_delete=models.CASCADE, null=True)
    timeout = models.SmallIntegerField(_("Timeout beeween questions"), null=True, blank=True, default=10)
    status = models.SmallIntegerField(_("Session status"), choices=STATUS, null=True, blank=True, default=STARTED)
    active = models.BooleanField(_("Active session"), default=True)
    rownumber = models.SmallIntegerField(_("Queries rows number"), null=True, blank=True, default=0)
    registered = models.SmallIntegerField(_("Registered gamers"), null=True, blank=True, default=0)

    class Meta:
        ordering = ['date', 'quiz']
        verbose_name = _("Session in progress")
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.id} - {self.date.strftime("%d/%m/%y %H:%M")} {self.quiz}'


class Reply(models.Model):
    session = models.ForeignKey(Session, verbose_name=_("Session"), on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, verbose_name=_("Gamer user"), on_delete=models.CASCADE, null=True)
    range = models.SmallIntegerField(_("Query range"), null=True, blank=True, default=0)
    response = models.SmallIntegerField(_("Response"), choices=Query.VALUE, null=True, blank=True, default=NO_ANSWER)
    result = models.BooleanField(_("Result"), default=False)

    class Meta:
        ordering = ['session', 'user', 'range']
        verbose_name = _("Session reply")
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.session_id}: {self.result}'


class Ranking(models.Model):
    session = models.ForeignKey(Session, verbose_name=_("Session"), on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, verbose_name=_("Gamer user"), on_delete=models.CASCADE, null=True)

    correct = models.SmallIntegerField(_("Correct answers"), null=True, blank=True, default=0)
    wrong = models.SmallIntegerField(_("Wrong answers"), null=True, blank=True, default=0)
    missing = models.SmallIntegerField(_("Missing answers"), null=True, blank=True, default=0)
    rank = models.SmallIntegerField(_("Rank"), null=True, blank=True, default=0)
    count = models.SmallIntegerField(_("Registered gamers"), null=True, blank=True, default=0)


    class Meta:
        ordering = ['session', 'rank', 'user']
        verbose_name = _("Ranking")
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.user.username}: {self.rank}'

