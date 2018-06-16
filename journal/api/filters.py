from django_filters import FilterSet, DateTimeFilter, CharFilter

from journal.api.fields import TimeStampField
from journal.api.models import HistoryRecord, Journal


class TimestampsFilter(DateTimeFilter):
    field_class = TimeStampField


class HistoryRecordFilter(FilterSet):
    from_date = TimestampsFilter(name='created_at', lookup_expr='gte')
    to_date = TimestampsFilter(name='created_at', lookup_expr='lte')
    pk = CharFilter(method='filter_pk')

    def filter_pk(self, queryset, name, value):
        pk = int(value)
        journal_id = int(self.data.get('journal'))
        journal = Journal.objects.get(id=journal_id)
        history_record_key = journal.history_record_key
        history_record_key_field = f'content__{history_record_key}'

        lookup = {
            'journal': journal,
            history_record_key_field: pk
        }

        history_records = queryset.filter(**lookup)
        return history_records

    class Meta:
        model = HistoryRecord
        fields = ['journal', 'action', 'from_date', 'to_date']