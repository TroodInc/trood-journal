from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from journal.api.filters import HistoryRecordFilter
from journal.api.models import Journal, HistoryRecord
from journal.api.serializers import JournalSerializer, HistoryRecordSerializer


class JournalViewSet(viewsets.ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.id)

    
class HistoryRecordViewSet(viewsets.ModelViewSet):
    queryset = HistoryRecord.objects.all()
    serializer_class = HistoryRecordSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = HistoryRecordFilter
    permission_classes = (IsAuthenticated,)


