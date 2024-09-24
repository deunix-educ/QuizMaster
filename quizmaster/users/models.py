#
# encoding: utf-8
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
#from django.db.models.signals import post_save
#from django.dispatch import receiver
from colorfield.fields import ColorField
from faker import Faker
from contrib import utils


fake = Faker(settings.LOCALE_CODE)
#Faker.seed(0)
#fake.seed_instance(0)


class User(AbstractUser):
    ANONYMOUS = 0
    GAMER = 10
    TESTER = 11
    CONTRIBUTOR=20
    STAFF = 90
    SUPER = 100

    ROLES = [
        (ANONYMOUS, '%s' % _("Anonymous user")),
        (GAMER, '%s' % _("Gamer user") ),
        (CONTRIBUTOR, '%s' % _("Contributor user")),
        (STAFF, '%s' % _("Staff authorized")),
        (SUPER, '%s' % _("Supervisor")),
    ]
    TESTER_ROLE = [(TESTER, '%s' % _("Gamer tester")),]

    role = models.PositiveSmallIntegerField(_("Gamer role"), choices=ROLES, null=True, blank=True, default=GAMER)
    uuid = models.CharField(_("Gamer uuid"), unique=True, max_length=32, null=True, blank=True)
    color = ColorField(_("Gamer color"), default='#F00F0F', null=True, blank=True)
    connected = models.BooleanField(_("Connected "), default=False)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.username:
            self.username = f'user_{self.user.id}'
        return super().save()


    @property
    def get_role_name(self):
        for k, v in self.ROLES + self.TESTER_ROLE:
            if k == self.role:
                return v

    @property
    def is_gamer(self):
        return True if self.role in [self.GAMER, self.TESTER] else False


    @property
    def is_contributor(self):
        return self.role in [self.CONTRIBUTOR, self.STAFF, self.SUPER]


    class Meta:
        ordering = ['username']
        verbose_name = _("User")
        verbose_name_plural = verbose_name


    def __str__(self):
        return f'{self.username}'


def new_user(role=User.GAMER):
    fake.seed_instance(utils.randint())
    username=fake.last_name().lower()
    try:
        Faker.seed(0)
        user = User.objects.get(username__exact=username)
        user.is_active = True
        user.connected = False
        user.save()
        return user
    except:
        return User.objects.create_user(
            username=username,
            password=username,
            role=role,
            color=fake.color(luminosity='light'),
            uuid=utils.get_apikey(12),
            is_active=True,
        )


