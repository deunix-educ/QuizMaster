#
# encoding: utf-8
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import DateFieldListFilter
from .models import (Topic, Query, Quiz, Queries, Session, Reply, Ranking)

class TopicAdmin(admin.ModelAdmin):
    list_display = ('title',)


class QueryAdmin(admin.ModelAdmin):
    list_display = ('_topic', 'description', 'boolean', 'level', 'expected', 'owner')
    list_filter  = ("topic", 'level')

    def _topic(self, instance):
        return instance.topic.title
    _topic.short_description = _("Topic")


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'level', 'active', 'code', '_owner', )
    list_filter  = ('level',)

    def _owner(self, instance):
        if instance and instance.owner:
            return instance.owner.username
    _owner.short_description = _("Owner")


class QueriesAdmin(admin.ModelAdmin):
    list_display = ('_quiz', '_query', 'range')
    list_filter  = ('quiz', 'quiz__level')

    def _quiz(self, instance):
        if instance and instance.quiz:
            return instance.quiz.title
    _quiz.short_description = _("Quiz")

    def _query(self, instance):
        if instance and instance.query and instance.query.topic:
            return instance.query.description[:64]
    _query.short_description = _("Query")


class ReplyAdmin(admin.ModelAdmin):
    list_display = ('_query', 'user', 'range', 'response', 'result')
    list_filter  = ('session', 'user')

    def _query(self, instance):
        return instance.session.quiz.title
    _query.short_description = _("Query")


class RankingAdmin(admin.ModelAdmin):
    list_display = ('_owner', 'correct', 'wrong', 'missing', 'rank', 'count')
    list_filter  = ('session', 'user')

    def _owner(self, instance):
        if instance and instance.user:
            return instance.user
    _owner.short_description = _("Owner")


class SessionAdmin(admin.ModelAdmin):
    list_display = ('date', 'id', '_quiz', 'status', 'rownumber', 'registered', '_owner')
    list_filter = (('date', DateFieldListFilter), )


    def _owner(self, instance):
        if instance and instance.owner:
            return instance.owner
    _owner.short_description = _("Owner")


    def _quiz(self, instance):
        if instance and instance.quiz:
            return instance.quiz.title
    _quiz.short_description = "Quiz"

    #def has_change_permission(self, request, obj=None):
    #    return False

    #def has_delete_permission(self, request, obj=None):
    #   return False

    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Session, SessionAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Query, QueryAdmin)
admin.site.register(Quiz, QuizAdmin)
admin.site.register(Queries, QueriesAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Ranking, RankingAdmin)

#
