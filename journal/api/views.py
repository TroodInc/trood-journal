from rest_framework import viewsets

from journal.api.models import Journal
from journal.api.serializers import JournalSerializer


class JournalViewSet(viewsets.ModelViewSet):
    queryset = Journal.objects.all()
    serializer_class = JournalSerializer
