from django_filters import rest_framework as filters
from rest_framework import viewsets, mixins
from rest_framework.viewsets import GenericViewSet

from journal.api.filters import HistoryRecordFilter
from journal.api.models import Journal, HistoryRecord
from journal.api.serializers import JournalSerializer, HistoryRecordSerializer


class JournalViewSet(viewsets.ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer

    
class HistoryRecordViewSet(viewsets.ModelViewSet):
    queryset = HistoryRecord.objects.all()
    serializer_class = HistoryRecordSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = HistoryRecordFilter
    http_method_names = ['get', 'post']

