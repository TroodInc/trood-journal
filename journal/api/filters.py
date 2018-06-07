from django_filters import FilterSet, DateTimeFilter

from journal.api.fields import TimeStampField
from journal.api.models import HistoryRecord


class TimestampsFilter(DateTimeFilter):
    field_class = TimeStampField


class HistoryRecordFilter(FilterSet):
    from_date = TimestampsFilter(name='created_at', lookup_expr='gte')
    to_date = TimestampsFilter(name='created_at', lookup_expr='lte')

    class Meta:
        model = HistoryRecord
        fields = ['journal', 'action', 'from_date', 'to_date']