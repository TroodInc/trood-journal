from rest_framework.test import APITestCase

from journal.api.models import HistoryRecord
from trood_auth_client.authentication import TroodUser

from journal.api.tests.factories import JournalFactory, HistoryRecordFactory

trood_user = TroodUser({
    "id": 1,
})


class HistoryApiCaseBehaveTest(APITestCase):
    def setUp(self):
        self.client.force_authenticate(user=trood_user)


    def test_create_retreive_history_records(self):
        input_data = {
            "id": "client",
            "name": "Clients journal",
            "type": 'objects',
            "target_key": "id",
            "actor_key": "id",
            "save_diff": True
        }
        response = self.client.post(f'/api/v1.0/journal/',
                                    data=input_data, format='json')

        journal_id = response.data['id']

        input_data = {
            "journal": journal_id,
            "action": "create",
            "actor": {"name": "John Doe", "id": 2},
            "content": {
                "id": 1,
                "name": "Client Inc.",
                "status": "new",
                "files": [1, 14]
            }

        }
        response = self.client.post(f'/api/v1.0/history/',
                                    data=input_data, format='json')

        input_data = {
            "journal": journal_id,
            "action": "update",
            "actor": {"name": "John Doe", "id": 2},
            "content": {
                "id": 1,
                "name": "Client Inc.",
                "status": "update",
                "files": [1]
            }

        }
        response = self.client.post(f'/api/v1.0/history/',
                                    data=input_data, format='json')

        response = self.client.get(
            f'/api/v1.0/history/?journal={journal_id}', format='json')

        history_records = HistoryRecord.objects.all()

        awaited_data = [{
            'id': history_records[0].id,
            'actor': {
                'id': 2,
                'name': 'John Doe'
            },
            'action': 'update',
            'v': 1,
            'ts': history_records[0].created_at.timestamp(),
            'diff': {
                'files': {'delete': [14]},
                'status': {'update': 'update'}
            },
            'journal': 'client',
            'revision': {
                'id': 1,
                'name': 'Client Inc.',
                'files': [1, 14],
                'status': 'new'
            }
        }, {
            'id': history_records[1].id,
            'actor': {
                'id': 2,
                'name': 'John Doe'
            },
            'action': 'create',
            'v': 0,
            'ts': history_records[1].created_at.timestamp(),
            'diff': None,
            'journal': 'client',
            'revision': {
                'id': 1, 'name': 'Client Inc.',
                'files': [1, 14],
                'status': 'new'}
        }]

        assert response.json() == awaited_data

    def test_save_remove_history_event(self):
        journal = JournalFactory.create(id='remove_test', target_key='id', name='Clients journal')

        HistoryRecordFactory.create(
            journal=journal, action='create', actor={'name': 'John Doe', 'id': 1},
            content={'name': 'Client Inc.', 'status': 'new', "id": 1}
        )

        # Push remove event with empty content
        #
        input_data = {
            "journal": journal.id,
            "action": "remove",
            "actor": {"name": "John Doe", "id": 2},
            "content": {'id': 1},
        }

        response = self.client.post(f'/api/v1.0/history/', data=input_data, format='json')
        assert response.status_code == 201

        record_id = response.json()['id']

        print(response.json())

        record = HistoryRecord.objects.get(id=record_id)

        assert record.prev is not None

