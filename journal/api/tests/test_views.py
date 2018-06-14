from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, \
    HTTP_204_NO_CONTENT
from rest_framework.test import APITestCase, APIClient

from journal.api.tests.factories import JournalFactory


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
