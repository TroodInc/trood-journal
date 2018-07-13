from django.core.exceptions import ObjectDoesNotExist
from django_filters import FilterSet, DateTimeFilter, CharFilter, exceptions

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
        journal = self.request.query_params.get('journal', None)

        if journal:
            pk = int(value)

            try:
                journal_object = Journal.objects.get(id=journal)
                target_key = journal_object.target_key

                return queryset.filter(**{f'content__{target_key}': pk})
            except ObjectDoesNotExist:
                raise exceptions.FieldError({"err": "Journal {} not found".format(journal)})

        else:
            raise exceptions.FieldError({"err": "You can't filter by `pk` without `journal` specifying ".format(journal)})

    class Meta:
        model = HistoryRecord
        fields = ['journal', 'action', 'from_date', 'to_date']