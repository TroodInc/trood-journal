from rest_framework import serializers

from journal.api.models import Journal, HistoryRecord
from journal.api.utils import make_diff


class JournalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Journal
        fields = ('id', 'target_key', 'name', 'type',
                  'actor_key', 'save_diff')


class HistoryRecordSerializer(serializers.ModelSerializer):
    v = serializers.IntegerField(source='version', read_only=True)
    ts = serializers.SerializerMethodField('get_created_at_timestamp')
    revision = serializers.SerializerMethodField()

    class Meta:
        model = HistoryRecord
        fields = ('id', 'actor', 'action', 'v', 'ts', 'diff',
                  'content', 'journal', 'revision')
        extra_kwargs = {'content': {'write_only': True},
                        'revision': {'read_only': True},
                        'actor': {'read_only': True},
                        'diff': {'read_only': True}}

    def get_created_at_timestamp(self, obj):
        return obj.created_at.timestamp() if obj.created_at else None

    def get_revision(self, obj):
        prev = obj.prev
        if not prev:
            return obj.content
        return prev.content

    def to_internal_value(self, data):
        """
        Skip default process to get raw data
        """
        input_data = data.copy()
        return input_data

    def create(self, validated_data):
        action = validated_data.get('action')
        actor = validated_data.get('actor')

        content = validated_data.get('content')

        journal_id = validated_data.get('journal')
        journal = Journal.objects.get(id=journal_id)

        target_id = content.get(journal.target_key)

        prev_history_record = HistoryRecord.objects.last_for_target(
            journal=journal,
            target_id=target_id
        )

        new_history_record = HistoryRecord(
            journal=journal,
            action=action,
            actor=actor,
            content=content,
        )

        if prev_history_record:
            new_history_record.prev = prev_history_record

        if journal.save_diff and prev_history_record:
        # Process current record in case if previous exists
            new_history_content = {}
            new_history_content.update(prev_history_record.content)
            new_history_content.update(content)

            diff = make_diff(prev_history_record.content, new_history_content)

            if diff:
                new_history_record.content = new_history_content
                new_history_record.version = prev_history_record.version + 1
                new_history_record.diff = diff
                new_history_record.save()
        else:
            new_history_record.save()

        return new_history_record



class HistoryRecordDiffSerializer(HistoryRecordSerializer):
    class Meta:
        model = HistoryRecord
        fields = ('actor', 'content',)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(data['content'])
        del data['content']
        return data

