from django.core.exceptions import ObjectDoesNotExist
from django_filters import FilterSet, DateTimeFilter, CharFilter, exceptions

from journal.api.fields import TimeStampField
from journal.api.models import HistoryRecord, Journal


class TimestampsFilter(DateTimeFilter):
    field_class = TimeStampField


class HistoryRecordFilter(FilterSet):
    from_date = TimestampsFilter(name='created_at', lookup_expr='gte')
    to_date = TimestampsFilter(name='created_at', lookup_expr='lte')
    pk = CharFilter(method='filter_custom_pk')
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
        fields = ['journal', 'action', 'from_date', 'to_date', 'actor']
