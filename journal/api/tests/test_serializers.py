from rest_framework.test import APITestCase

from journal.api.serializers import HistoryRecordSerializer
from journal.api.tests.factories import JournalFactory, HistoryRecordFactory


class HistoryRecordSerializerTestCase(APITestCase):
    def test_serialize_ok(self):
        journal = JournalFactory.create(alias='clients',
                                        name='Clients journal')
        hr = HistoryRecordFactory.create(journal=journal,
                                         action='create',
                                         actor={'name': 'John Doe', 'id': 2},
                                         content={'name': 'Client Inc.',
                                                  'status': 'new', 'files': [1, 14]})
        serialized_data = HistoryRecordSerializer(instance=hr).data
        assert hr.action == serialized_data['_action']
        assert hr.journal.alias == serialized_data['_type']
        assert hr.version == serialized_data['_v']
        assert hr.created_at.timestamp() == serialized_data['_ts']

    def test_to_internal_value_ok(self):
        input_data = {
            "_action": "create",
            "_actor": {"name": "John Doe", "id": 2},
            "name": "Client Inc.",
            "status": "new",
            "files": [1, 14],
        }
        output_data = {
            "_action": "create",
            "_actor": {"name": "John Doe", "id": 2},
            "content": {"name": "Client Inc.", "status": "new", "files": [1, 14]}
        }
        serializer = HistoryRecordSerializer(data=input_data)
        serializer.is_valid()
        validated_data = serializer.validated_data
        assert validated_data == output_data

    def test_to_representation_ok(self):
        journal = JournalFactory.create(alias='clients',
                                        name='Clients journal')
        hr = HistoryRecordFactory.create(journal=journal,
                                         action='create',
                                         actor={'name': 'John Doe', 'id': 2},
                                         content={'name': 'Client Inc.',
                                                  'status': 'new',
                                                  'files': [1, 14]},
                                         diff={
                                             'files': {'delete': [14]},
                                             'status': {'update': 'update'},
                                         })
        serializer_data = HistoryRecordSerializer(instance=hr).data
        awaited_data = {'_actor': {'name': 'John Doe', 'id': 2},
                        '_action': 'create',
                        '_type': journal.alias,
                        '_v': 0,
                        '_ts': hr.created_at.timestamp(),
                        'name': 'Client Inc.',
                        'status': 'new',
                        'files': [1, 14],
                        'journal': hr.journal.id,
                        '_diff': {
                            'files': {'delete': [14]},
                            'status': {'update': 'update'},
                        }
        }

        assert serializer_data == awaited_data
