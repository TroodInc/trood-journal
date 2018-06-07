from rest_framework import serializers

from journal.api.models import Journal, HistoryRecord
from journal.api.utils import make_diff


class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ('id', 'alias', 'history_record_key', 'name', 'type',
                  'history_record_actor', 'save_diff')


class HistoryRecordSerializer(serializers.ModelSerializer):
    _action = serializers.CharField(source='action')
    _type = serializers.CharField(source='journal.alias', read_only=True)
    _v = serializers.IntegerField(source='version', read_only=True)
    _ts = serializers.SerializerMethodField('get_created_at_timestamp')
    _actor = serializers.JSONField(source='actor', read_only=True)
    _diff = serializers.JSONField(source='diff', read_only=True)

    class Meta:
        model = HistoryRecord
        fields = ('_actor', '_action', '_type', '_v', '_ts', '_diff',
                  'content', 'journal')
        extra_kwargs = {'content': {'read_only': True}}


    def get_created_at_timestamp(self, obj):
        return obj.created_at.timestamp()
    
    def to_internal_value(self, data):
        input_data = data.copy()
        content = {}
        for k in data.keys():
            # Put fields strictly related to object to content dict
            if not k.startswith('_'):
                content[k] = data[k]
                # And drop them from input data
                del input_data[k]
        input_data['content'] = content
        return input_data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(data['content'])
        del data['content']
        return data

    def create(self, validated_data):
        action = validated_data.get('_action')
        actor = validated_data.get('_actor')

        content = validated_data.get('content')
        journal_id = content.get('journal')
        journal = Journal.objects.get(id=journal_id)

        prev_history_record = None
        if journal.history_records.count() > 0:
            prev_history_record = journal.history_records.first()

        new_history_record = HistoryRecord.objects.create(
            journal=journal,
            action=action,
            actor=actor,
            content=content,
        )
        if prev_history_record:
            prev_history_record_dict = HistoryRecordDiffSerializer(
                instance=prev_history_record
            ).data
            new_history_record_dict = HistoryRecordDiffSerializer(
                instance=new_history_record
            ).data
            diff = make_diff(prev_history_record_dict, new_history_record_dict)
            new_history_record.diff = diff

            new_history_record.version = prev_history_record.version + 1

            new_history_record.save()

        return new_history_record


class HistoryRecordDiffSerializer(HistoryRecordSerializer):
    class Meta:
        model = HistoryRecord
        fields = ('_actor', 'content',)

