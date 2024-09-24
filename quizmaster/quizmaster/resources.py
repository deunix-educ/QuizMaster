#
# encoding: utf-8

from import_export import resources
from .models import Query, Ranking, Queries


class QueryResourceImport(resources.ModelResource):
    class Meta:
        model = Query
        fields = ['description', 'boolean', 'A', 'B', 'C', 'D', 'E', 'F', 'expected',]
        export_order = fields
        exclude = ['id', 'owner', 'topic', 'level',]


class RankingResource(resources.ModelResource):
    class Meta:
        model = Ranking
        fields = ['session', 'session__quiz__title', 'user__username', 'rank', 'correct', 'wrong', 'missing']
        export_order = fields
        exclude = ['id',]

class QueriesResource(resources.ModelResource):
    class Meta:
        model = Queries
        fields = ['query__description', 'query__boolean', 'query__A', 'query__B', 'query__C', 'query__D', 'query__E', 'query__F', 'query__expected']
        export_order = fields