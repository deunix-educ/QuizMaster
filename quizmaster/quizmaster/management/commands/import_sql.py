#
# encoding: utf-8
#import sys
#import os, pathlib
#from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.management import BaseCommand
from quizmaster.models import Topic

TOPICS = [
    _('True or false'),
    _('Computer science'),
    _('Various'),
    _('Science'),
    _('History'),
    _('Geography'),
    _('General culture'),
    _('News'),
    _('Mathematics'),
]

def create_topics():
    for topic in TOPICS:
        print('>>', topic)
        Topic.objects.create(title=topic)

class Command(BaseCommand):

    def handle(self, *args, **options):
        try:
            create_topics()

        except Exception as e:
            print(f'Command error {e}', flush=True)
