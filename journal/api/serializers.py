from rest_framework import serializers

from journal.api.models import Journal


class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ('id', 'alias', 'history_record_key', 'name', 'type',
                  'history_record_actor', 'save_diff')