from time import sleep

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT
from rest_framework.test import APITestCase, APIClient

from journal.api.models import HistoryRecord
from journal.api.tests.factories import JournalFactory, HistoryRecordFactory
from trood_auth_client.authentication import TroodUser

trood_user = TroodUser({
    "id": 1,
})

TS_DELTA = 2


def _initialize_journal_data():
    journal = JournalFactory.create(id='lead', name='Leads journal')
    hr1 = HistoryRecordFactory.create(
        journal=journal, action='create', actor={'name': 'John Doe', 'id': 2},
        content={'name': 'Client Inc.', 'status': 'new', 'files': [1, 14]}
    )

    sleep(3)

    hr2 = HistoryRecordFactory.create(journal=journal,
                                      action='update',
                                      actor={'name': 'John Doe', 'id': 2},
                                      content={'name': 'Client Inc.',
                                               'status': 'update',
                                               'files': [1],
                                               'comments': [
                                                   'Hello worlds']})
    to_ret = {
        'journal': journal,
        'hr1': hr1,
        'hr2': hr2,
    }

    return to_ret


class JournalViewSetTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=trood_user)

    def test_create_journal_ok(self):
        data = {
            "id": "client",
            "name": "Clients journal",
            "type": "objects",
            "target_key": "id",
            "actor_key": "id",
            "save_diff": True
        }
        response = self.client.post('/api/v1.0/journal/', data=data, format='json')
        assert response.status_code == HTTP_201_CREATED

    def test_get_journals_ok(self):
        journal_1 = JournalFactory.create(id='client', name='Clients journal')
        journal_2 = JournalFactory.create(id='lead', name='Leads journal')

        response = self.client.get('/api/v1.0/journal/')
        assert response.status_code == HTTP_200_OK
        assert len(response.data) == 2

    def test_update_journal_ok(self):
        journal = JournalFactory.create(id='lead', name='Leads journal')

        response = self.client.patch(f'/api/v1.0/journal/{journal.id}/',
                                     data={'name': 'superleads'}, format='json')
        assert response.status_code == HTTP_200_OK

    def test_delete_journal_ok(self):
        journal = JournalFactory.create(id='lead',
                                        name='Leads journal')
        response = self.client.delete(f'/api/v1.0/journal/{journal.id}/', format='json')
        assert response.status_code == HTTP_204_NO_CONTENT

    def test_fetch_history_empty_200(self):
        journal = JournalFactory.create(id='lead', name='Leads journal')

        response = self.client.get(f'/api/v1.0/history/?journal={journal.id}', format='json')

        assert response.status_code == HTTP_200_OK

    def test_fetch_history_list(self):
        journal = JournalFactory.create(id='lead', name='Leads journal')

        hr1 = HistoryRecordFactory.create(
            journal=journal, action='create',
            actor={'name': 'John Doe', 'id': 2},
            content={'name': 'Client Inc.', 'status': 'new', 'files': [1, 14]}
        )

        hr2 = HistoryRecordFactory.create(
            journal=journal, action='update',
            actor={'name': 'John Doe', 'id': 2},
            content={'name': 'Client Inc.', 'status': 'update', 'files': [1], 'comments': ['Hello worlds']}
        )

        response = self.client.get(
            f'/api/v1.0/history/?journal={journal.id}',
            format='json')
        assert response.status_code == HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_by_created_at_all(self):
        data = _initialize_journal_data()
        from_date = int(data['hr1'].created_at.timestamp() - TS_DELTA)
        to_date = int(data['hr2'].created_at.timestamp() + TS_DELTA)
        response = self.client.get(
            f'/api/v1.0/history/?from_date={from_date}&to_date={to_date}',
            format='json')
        assert response.status_code == HTTP_200_OK
        assert len(response.data) == 2

    def test_filter_by_created_at_one(self):
        data = _initialize_journal_data()
        from_date = int(data['hr1'].created_at.timestamp() - TS_DELTA)
        to_date = int(data['hr2'].created_at.timestamp() - TS_DELTA)
        response = self.client.get(
            f'/api/v1.0/history/?from_date={from_date}&to_date={to_date}',
            format='json')
        assert response.status_code == HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_by_journal_and_pk(self):
        client_journal = JournalFactory.create(id='client', name='Clients journal', target_key='target_id')

        hr = HistoryRecordFactory.create(
            journal=client_journal, action='create',
            actor={'name': 'John Doe', 'id': 2},
            content={'name': 'Client Inc.', 'status': 'new'}
        )

        lead_journal = JournalFactory.create(id='lead', name='Leads journal', target_key='target_id')

        # Create history records for first lead
        hr1 = HistoryRecordFactory.create(
            journal=lead_journal, action='create',
            actor={'name': 'John Doe', 'id': 2},
            content={'name': 'Client Inc.', 'status': 'new', 'target_id': 1, 'files': [1, 14]}
        )

        hr2 = HistoryRecordFactory.create(
            journal=lead_journal, action='update',
            actor={'name': 'John Doe', 'id': 2},
            content={'name': 'Client Inc.', 'status': 'update', 'target_id': 1, 'files': [1], 'comments': ['Hello worlds']}
        )

        hr3 = HistoryRecordFactory.create(
            journal=lead_journal, action='update',
            actor={'name': 'John Doe', 'id': 2},
            content={'name': 'Client Inc.', 'status': 'update', 'target_id': 1, 'files': [1], 'comments': ['Hello worlds', 'Bye worlds']}
        )

        # Create history records for second lead
        hr4 = HistoryRecordFactory.create(
            journal=lead_journal, action='create',
            actor={'name': 'Alice Cup', 'id': 3},
            content={'name': 'Megaclient', 'status': 'new', 'target_id': 2}
        )

        hr5 = HistoryRecordFactory.create(
            journal=lead_journal, action='update',
            actor={'name': 'Alice Cup', 'id': 3},
            content={'name': 'Megaclient', 'status': 'update', 'target_id': 2, 'files': [2, 3]}
        )

        response = self.client.get(f'/api/v1.0/history/?journal={lead_journal.id}&pk={1}', format='json')

        assert response.status_code == HTTP_200_OK
        assert len(response.data) == 3

    def test_filter_by_journal_and_actor(self):
        client_journal = JournalFactory.create(id='client', name='Clients journal')

        hr = HistoryRecordFactory.create(
            journal=client_journal, action='create',
            actor={'name': 'John Doe', 'id': 1},
            content={'name': 'Client Inc.', 'status': 'new'}
        )

        hr2 = HistoryRecordFactory.create(
            journal=client_journal, action='create',
            actor={'name': 'Jane Snow', 'id': 2},
            content={'name': 'Bottles CO.', 'status': 'new'}
        )

        response = self.client.get('/api/v1.0/history/', data={'journal': 'client', "actor": 2}, format='json')

        assert response.status_code == HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == hr2.id


class HistoryRecordViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=trood_user)

    def test_create_history_record_ok(self):
        journal = JournalFactory.create(id='lead', name='Leads journal')

        data = {
            "journal": "lead",
            "action": "update",
            "actor": {"name": "John Doe", "id": 2},
            "content": {
                "id": 1,
                "name": "Client Inc.",
                "status": "in_work",
                "files": [1],
                "comments": [12]
            }
        }
        response = self.client.post('/api/v1.0/history/', data=data, format='json')
        assert response.status_code == HTTP_201_CREATED

    def test_create_history_record_diff_ok(self):
        journal = JournalFactory.create(id='client', target_key='id', name='Clients journal')
        input_data = {
            "journal": journal.id,
            "action": "create",
            "actor": {"name": "John Doe", "id": 2},
            "content": {
                "name": "Client Inc.",
                "status": "new",
                "id": 1,
                "files": [1, 14]
            }

        }
        response = self.client.post(f'/api/v1.0/history/', data=input_data, format='json')
        assert response.status_code == 201

        input_data = {
            "journal": journal.id,
            "action": "update",
            "actor": {"name": "John Doe", "id": 2},
            "content": {
                "name": "Client Inc.",
                "status": "update",
                "id": 1,
                "files": [1],
            }
        }
        response = self.client.post(f'/api/v1.0/history/', data=input_data, format='json')
        assert response.status_code == 201

        response = self.client.get(f'/api/v1.0/history/?journal={journal.id}', format='json')

        last_history_record = HistoryRecord.objects.first()
        diff = last_history_record.diff
        awaited_diff = {
            'files': {'delete': [14]},
            'status': {'update': 'update'},
        }
        assert diff == awaited_diff
