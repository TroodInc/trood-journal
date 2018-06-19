from time import sleep

from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, \
    HTTP_204_NO_CONTENT, HTTP_301_MOVED_PERMANENTLY, HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.test import APITestCase, APIClient

from journal.api.models import HistoryRecord
from journal.api.tests.factories import JournalFactory, HistoryRecordFactory


TS_DELTA = 2


def _initialize_journal_data():
    journal = JournalFactory.create(alias='leads',
                                    name='Leads journal')
    hr1 = HistoryRecordFactory.create(journal=journal,
                                      action='create',
                                      actor={'name': 'John Doe', 'id': 2},
                                      content={'name': 'Client Inc.',
                                               'status': 'new',
                                               'files': [1, 14]})

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

    def test_create_journal_ok(self):
        data = {
            "alias": "clients",
            "name": "Clients journal",
            "type": "objects",
            "history_record_key": "id",
            "history_record_actor": "actor.id",
            "save_diff": True
        }
        response = self.client.post('/api/v1.0/journals/', data=data, format='json')
        assert response.status_code == HTTP_201_CREATED

    def test_get_journals_ok(self):
        journal_1 = JournalFactory.create(alias='clients', name='Clients journal')
        journal_2 = JournalFactory.create(alias='leads', name='Leads journal')

        response = self.client.get('/api/v1.0/journals/')
        assert response.status_code == HTTP_200_OK
        assert len(response.data) == 2

    def test_update_journal_ok(self):
        journal = JournalFactory.create(alias='leads', name='Leads journal')

        response = self.client.patch(f'/api/v1.0/journals/{journal.id}/',
                                     data={'name': 'superleads'}, format='json')
        assert response.status_code == HTTP_200_OK

    def test_delete_journal_ok(self):
        journal = JournalFactory.create(alias='leads',
                                        name='Leads journal')
        response = self.client.delete(f'/api/v1.0/journals/{journal.id}/', format='json')
        assert response.status_code == HTTP_204_NO_CONTENT

    def test_fetch_history_empty_200(self):
        journal = JournalFactory.create(alias='leads',
                                        name='Leads journal')
        response = self.client.get(f'/api/v1.0/history/?journal={journal.id}',
                                   format='json')
        assert response.status_code == HTTP_200_OK

    def test_fetch_history_list(self):
        journal = JournalFactory.create(alias='lead',
                                        name='Leads journal')
        hr1 = HistoryRecordFactory.create(journal=journal,
                                          action='create',
                                          actor={'name': 'John Doe', 'id': 2},
                                          content={'name': 'Client Inc.',
                                                   'status': 'new',
                                                   'files': [1, 14]})

        hr2 = HistoryRecordFactory.create(journal=journal,
                                          action='update',
                                          actor={'name': 'John Doe', 'id': 2},
                                          content={'name': 'Client Inc.',
                                                   'status': 'update',
                                                   'files': [1],
                                                   'comments': [
                                                       'Hello worlds']})
        response = self.client.get(
            f'/api/v1.0/history/?journal={journal.alias}',
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
        client_journal = JournalFactory.create(alias='client',
                                        name='Clients journal',
                                        history_record_key='target_id')

        hr = HistoryRecordFactory.create(journal=client_journal,
                                          action='create',
                                          actor={'name': 'John Doe', 'id': 2},
                                          content={'name': 'Client Inc.',
                                                   'status': 'new'})

        lead_journal = JournalFactory.create(alias='lead',
                                        name='Leads journal',
                                        history_record_key='target_id')

        # Create history records for first lead
        hr1 = HistoryRecordFactory.create(journal=lead_journal,
                                          action='create',
                                          actor={'name': 'John Doe', 'id': 2},
                                          content={'name': 'Client Inc.',
                                                   'status': 'new',
                                                   'target_id': 1,
                                                   'files': [1, 14]})

        hr2 = HistoryRecordFactory.create(journal=lead_journal,
                                          action='update',
                                          actor={'name': 'John Doe', 'id': 2},
                                          content={'name': 'Client Inc.',
                                                   'status': 'update',
                                                   'target_id': 1,
                                                   'files': [1],
                                                   'comments': [
                                                       'Hello worlds']})
        hr3 = HistoryRecordFactory.create(journal=lead_journal,
                                          action='update',
                                          actor={'name': 'John Doe', 'id': 2},
                                          content={'name': 'Client Inc.',
                                                   'status': 'update',
                                                   'target_id': 1,
                                                   'files': [1],
                                                   'comments': ['Hello worlds',
                                                                'Bye worlds']})

        # Create history records for second lead
        hr4 = HistoryRecordFactory.create(journal=lead_journal,
                                          action='create',
                                          actor={'name': 'Alice Cup', 'id': 3},
                                          content={'name': 'Megaclient',
                                                   'status': 'new',
                                                   'target_id': 2})

        hr5 = HistoryRecordFactory.create(journal=lead_journal,
                                          action='update',
                                          actor={'name': 'Alice Cup', 'id': 3},
                                          content={'name': 'Megaclient',
                                                   'status': 'update',
                                                   'target_id': 2,
                                                   'files': [2, 3]})
        response = self.client.get(
            f'/api/v1.0/history/?journal={lead_journal.alias}&pk={1}',
            format='json')

        assert response.status_code == HTTP_200_OK
        assert len(response.data) == 3


class HistoryRecordViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_create_history_record_ok(self):
        journal = JournalFactory.create(alias='clients',
                                        history_record_key='target_id',
                                        name='Clients journal')

        input_data = {
            "journal": journal.id,
            "_action": "create",
            "_actor": {"name": "John Doe", "id": 2},
            "name": "Client Inc.",
            "status": "new",
            "target_id": 1,
            "files": [1, 14],
        }
        response = self.client.post(f'/api/v1.0/history/',
                                    data=input_data, format='json')
        assert response.status_code == 201

    def test_create_history_record_diff_ok(self):
        journal = JournalFactory.create(alias='clients',
                                        history_record_key='target_id',
                                        name='Clients journal')

        input_data = {
            "journal": journal.id,
            "_action": "create",
            "_actor": {"name": "John Doe", "id": 2},
            "name": "Client Inc.",
            "status": "new",
            "target_id": 1,
            "files": [1, 14],
        }
        response = self.client.post(f'/api/v1.0/history/',
                                    data=input_data, format='json')
        assert response.status_code == 201

        input_data = {
            "journal": journal.id,
            "_action": "update",
            "_actor": {"name": "John Doe", "id": 2},
            "name": "Client Inc.",
            "status": "update",
            "target_id": 1,
            "files": [1],
        }
        response = self.client.post(f'/api/v1.0/history/',
                                    data=input_data, format='json')
        assert response.status_code == 201

        last_history_record = HistoryRecord.objects.first()
        diff = last_history_record.diff
        awaited_diff = {
            'files': {'delete': [14]},
            'status': {'update': 'update'},
        }
        assert diff == awaited_diff

    # def test_prevent_patch_history(self):
    #     journal = JournalFactory.create(alias='clients',
    #                                     name='Clients journal')
    #     hr = HistoryRecordFactory.create(journal=journal,
    #                                      action='create',
    #                                      actor={'name': 'John Doe', 'id': 2},
    #                                      content={'name': 'Client Inc.',
    #                                               'status': 'new',
    #                                               'files': [1, 14]},
    #                                      diff={
    #                                          'files': {'delete': [1]},
    #                                          'status': {'update': 'update'},
    #                                          '_action': {'update': 'update'}
    #                                      })
    #     input_data = {
    #         "_journal": journal.id,
    #         "_action": "create",
    #     }
    #     response = self.client.post(f'/api/v1.0/history/{hr.id}/',
    #                                 data=input_data, format='json')
    #     assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    #
    # def test_prevent_put_history(self):
    #     journal = JournalFactory.create(alias='clients',
    #                                     name='Clients journal')
    #     hr = HistoryRecordFactory.create(journal=journal,
    #                                      action='create',
    #                                      actor={'name': 'John Doe', 'id': 2},
    #                                      content={'name': 'Client Inc.',
    #                                               'status': 'new',
    #                                               'files': [1, 14]},
    #                                      diff={
    #                                          'files': {'delete': [1]},
    #                                          'status': {'update': 'update'},
    #                                          '_action': {'update': 'update'}
    #                                      })
    #     input_data = {
    #         "_journal": journal.id,
    #         "_action": "create",
    #         "_actor": {"name": "John Doe", "id": 2},
    #         "name": "Client Inc.",
    #         "status": "new",
    #         "files": [1, 14],
    #     }
    #     response = self.client.post(f'/api/v1.0/history/{hr.id}/',
    #                                 data=input_data, format='json')
    #     assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED
    #
    # def test_prevent_delete_history(self):
    #     journal = JournalFactory.create(alias='clients',
    #                                     name='Clients journal')
    #     hr = HistoryRecordFactory.create(journal=journal,
    #                                      action='create',
    #                                      actor={'name': 'John Doe',
    #                                             'id': 2},
    #                                      content={'name': 'Client Inc.',
    #                                               'status': 'new',
    #                                               'files': [1, 14]},
    #                                      diff={
    #                                          'files': {'delete': [1]},
    #                                          'status': {'update': 'update'},
    #                                          '_action': {'update': 'update'}
    #                                      })
    #     response = self.client.delete(f'/api/v1.0/history/{hr.id}/')
    #     assert response.status_code == HTTP_405_METHOD_NOT_ALLOWED