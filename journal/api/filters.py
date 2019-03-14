from functools import reduce
from operator import __or__, __and__

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import ObjectDoesNotExist
from django_filters import FilterSet, DateTimeFilter, CharFilter, exceptions, Filter
from django_filters.constants import EMPTY_VALUES

from django.db.models import Q
from pyparsing import Literal, Word, alphas, alphanums, Group, Forward, delimitedList, ParseException
from rest_framework.filters import BaseFilterBackend

from journal.api.fields import TimeStampField
from journal.api.models import HistoryRecord, Journal


class TimestampsFilter(DateTimeFilter):
    field_class = TimeStampField


class JSONFieldFilter(Filter):

    def filter(self, qs, value):
        print(self.field_name)
        print(self.lookup_expr)
        print(value)

        if value in EMPTY_VALUES:
            return qs
        if self.distinct:
            qs = qs.distinct()
        lookup = '%s__%s' % (self.field_name, self.lookup_expr)
        qs = self.get_method(qs)(**{lookup: value})
        return qs


class HistoryRecordFilter(FilterSet):
    from_date = TimestampsFilter(name='created_at', lookup_expr='gte')
    to_date = TimestampsFilter(name='created_at', lookup_expr='lte')
    pk = CharFilter(method='filter_custom_pk')
    # revision = Filter(name='prev__content')
    actor = CharFilter(method='filter_custom_pk')
    journal = CharFilter(name='journal__id', lookup_expr='exact')

    def filter_custom_pk(self, queryset, name, value):
        journal = self.request.query_params.get('journal', None)

        if journal:
            try:
                journal_object = Journal.objects.get(id=journal)

                if name == "pk":
                    key = journal_object.target_key
                    field = "content"
                if name == "actor":
                    key = journal_object.actor_key
                    field = "actor"

                return queryset.filter(**{f'{field}__{key}': int(value)})
            except ObjectDoesNotExist:
                raise exceptions.FieldError({"err": "Journal {} not found".format(journal)})

        else:
            raise exceptions.FieldError({"err": "You can't filter by `pk` without `journal` specifying ".format(journal)})

    class Meta:
        model = HistoryRecord
        fields = ['journal', 'action', 'from_date', 'to_date', 'actor', 'content']
        filter_overrides = {
            JSONField: {
                'filter_class': JSONFieldFilter,
            }
        }


class RQLFilterBackend(BaseFilterBackend):
    """
    Filter that uses a RQL query.

    The RQL query is expected to be passed as a querystring parameter.
    The RQL_FILTER_QUERY_PARAM setting (which defaults to 'rql') specifies the
    name of the querystring parameter used.
    """

    AND = Literal('and').setParseAction(lambda: 'AND')
    OR = Literal('or').setParseAction(lambda: 'OR')

    EQ = Literal('eq').setParseAction(lambda: 'exact')
    NE = Literal('ne').setParseAction(lambda: 'ne')
    GE = Literal('ge').setParseAction(lambda: 'gte')
    GT = Literal('gt').setParseAction(lambda: 'gt')
    LE = Literal('le').setParseAction(lambda: 'lte')
    LT = Literal('lt').setParseAction(lambda: 'lt')
    IN = Literal('in').setParseAction(lambda: 'in')

    FN = EQ | NE | GE | GT | LE | LT | IN

    OB = Literal('(').suppress()
    CB = Literal(')').suppress()
    CM = Literal(',').suppress()

    NAME = Word(alphas + '_.', alphanums + '_.')
    VALUE = Word(alphanums) | Literal('"').suppress() + Word(alphanums + ' ') + Literal('"').suppress()

    ARRAY = OB + delimitedList(VALUE, ',') + CB
    ARRAY = ARRAY.setParseAction(lambda s, loc, toks: [toks])

    SIMPLE_COND = FN + OB + NAME + CM + (VALUE | ARRAY) + CB

    NESTED_CONDS = Forward()
    AGGREGATE = (AND | OR) + OB + delimitedList(NESTED_CONDS, ',') + CB
    COND = Group(SIMPLE_COND) | Group(AGGREGATE)
    NESTED_CONDS << COND

    QUERY = NESTED_CONDS

    query_param = getattr(settings, 'RQL_FILTER_QUERY_PARAM', 'rql')

    @classmethod
    def parse_rql(cls, rql):
        try:
            parse_results = cls.QUERY.parseString(rql)
        except ParseException:
            raise
        return parse_results.asList()

    @classmethod
    def make_query(cls, data):
        conditions = []
        for fn in data:
            if fn[0] == 'AND':
                res = cls.make_query(fn[1:])
                conditions.append(reduce(__and__, res) if res else [])
            elif fn[0] == 'OR':
                res = cls.make_query(fn[1:])
                conditions.append(reduce(__or__, res) if res else [])
            else:
                field = '{}__{}'.format(fn[1].replace('.', '__'), fn[0])
                conditions.append(Q(**{field: convert_numeric(fn[2])}))
        return conditions

    def filter_queryset(self, request, queryset, view):
        qs = queryset

        if self.query_param in request.GET:
            if len(request.GET[self.query_param]):
                condition = self.make_query(
                    self.parse_rql(request.GET[self.query_param])
                )

                print(condition)

                qs = qs.filter(*condition)

        return qs


def convert_numeric(val):
    if type(val) is str:
        if val.isnumeric():
            if '.' in val:
                val = float(val)
            else:
                val = int(val)
    elif type(val) is list:
        for i, a in enumerate(val):
            val[i] = convert_numeric(a)

    return val
