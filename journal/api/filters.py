from django_filters import FilterSet, DateTimeFilter, CharFilter

from journal.api.fields import TimeStampField
from journal.api.models import HistoryRecord, Journal


class TimestampsFilter(DateTimeFilter):
    field_class = TimeStampField


class HistoryRecordFilter(FilterSet):
    from_date = TimestampsFilter(name='created_at', lookup_expr='gte')
    to_date = TimestampsFilter(name='created_at', lookup_expr='lte')
    pk = CharFilter(method='filter_pk')
    journal = CharFilter(name='journal__id', lookup_expr='exact')

    def filter_pk(self, queryset, name, value):
        pk = int(value)
        journal = queryset.first().journal
        target_key = journal.target_key
        content_target_key = f'content__{target_key}'

        lookup = {
            'journal': journal,
            content_target_key: pk
        }

        history_records = queryset.filter(**lookup)
        return history_records

    class Meta:
        model = HistoryRecord
        fields = ['journal', 'action', 'from_date', 'to_date']