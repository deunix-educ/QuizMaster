'''
Created on 29 mars 2023

@author: denis
'''
from datetime import timedelta
from dateutil.relativedelta import relativedelta

from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now

def _truncate(dt):
    return dt.date()

yn_choices = (
    (True, _("Valid date")),
    (False, _("Invalid date"))
)

active_choices = (
    (True, _("Active")),
    (False, _("Inactive"))
)

DF_CHOICES = [
    ('today', _('Today')),
    ('yesterday', _('Yesterday')),
    ('week', _('From 1 week')),
    ('week2',  _('From 2 weeks')),
    ('month',  _('From 1 month')),
    ('month3', _('From 3 months')),
    ('month6', _('From 6 months')),
    ('year', _('From 1 year')),
]

DF_FILTERS = {
    'today': lambda qs, name: qs.filter(**{
        '%s__year' % name: now().year,
        '%s__month' % name: now().month,
        '%s__day' % name: now().day
    }),
    'yesterday': lambda qs, name: qs.filter(**{
        '%s__year' % name: (now() - timedelta(days=1)).year,
        '%s__month' % name: (now() - timedelta(days=1)).month,
        '%s__day' % name: (now() - timedelta(days=1)).day,
    }),
    'week': lambda qs, name: qs.filter(**{
        '%s__gte' % name: _truncate(now() - timedelta(days=7)),
    }),
    'week2': lambda qs, name: qs.filter(**{
        '%s__gte' % name: _truncate(now() - timedelta(days=15)),
    }),
    'month': lambda qs, name: qs.filter(**{
        '%s__gte' % name: _truncate(now() - relativedelta(months=1)),
    }),
    'month3': lambda qs, name: qs.filter(**{
        '%s__gte' % name: _truncate(now() - relativedelta(months=3)),
    }),
    'month6': lambda qs, name: qs.filter(**{
        '%s__gte' % name: _truncate(now() - relativedelta(months=6)),
        '%s__lt' % name: _truncate(now() + timedelta(days=1)),
    }),
    'year': lambda qs, name: qs.filter(**{
        '%s__gte' % name: _truncate(now() - relativedelta(years=1)),
    }),
}

