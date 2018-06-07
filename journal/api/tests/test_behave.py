from rest_framework.test import APITestCase

from journal.api.models import HistoryRecord
from journal.api.tests.factories import JournalFactory


class HistoryApiCaseBehaveTest(APITestCase):
    def test_create_retreive_history_records(self):
        input_data = {
            "alias": "clients",
            "name": "Clients journal",
            "type": 'objects',
            "history_record_key": "id",
            "history_record_actor": "actor.id",
            "save_diff": True
        }
        response = self.client.post(f'/api/v1.0/journals/',
                                    data=input_data, format='json')

        journal_id = response.data['id']

        input_data = {
            "journal": journal_id,
            "_action": "create",
            "_actor": {"name": "John Doe", "id": 2},
            "name": "Client Inc.",
            "status": "new",
            "files": [1, 14],
        }
        response = self.client.post(f'/api/v1.0/history/',
                                      data=input_data, format='json')

        input_data = {
            "journal": journal_id,
            "_action": "update",
            "_actor": {"name": "John Doe", "id": 2},
            "name": "Client Inc.",
            "status": "update",
            "files": [1],
        }
        response = self.client.post(f'/api/v1.0/history/',
                                      data=input_data, format='json')

        response = self.client.get(
            f'/api/v1.0/history/?journal={journal_id}', format='json')

        history_records = HistoryRecord.objects.all()

        awaited_data = [
            {
                '_actor': {'id': 2, 'name': 'John Doe'},
                '_action': 'update',
                '_type': 'clients',
                '_v': 1,
                '_ts': history_records.first().created_at.timestamp(),
                '_diff': {'files': {'delete': [14]},
                          'status': {'update': 'update'}},
                'journal': 1,
                'name': 'Client Inc.',
                'files': [1],
                'status': 'update'
            },
            {
                '_actor': {'id': 2, 'name': 'John Doe'},
                '_action': 'create',
                '_type': 'clients',
                '_v': 0,
                '_ts': history_records.last().created_at.timestamp(),
                '_diff': None,
                'journal': 1,
                'name': 'Client Inc.',
                'files': [1, 14],
                'status': 'new'
             }
        ]

        assert response.json() == awaited_data
