from django.test import testcases

from journal.api.serializers import HistoryRecordDiffSerializer
from journal.api.tests.factories import JournalFactory, HistoryRecordFactory
from journal.api.utils import make_diff


class HistoryRecordViewSetTestCase(testcases.TestCase):
    def test_make_diff_ok(self):
        journal = JournalFactory.create(id='client',
                                        name='Clients journal')
        hr1 = HistoryRecordFactory.create(journal=journal,
                                         action='create',
                                         actor={'name': 'John Doe', 'id': 2},
                                         content={'name': 'Client Inc.',
                                                  'status': 'new',
                                                  'related': {
                                                      '_object': 'corporation',
                                                      'id': 'Test Co.'
                                                  },
                                                  'files': [2, 14]})

        hr2 = HistoryRecordFactory.create(journal=journal,
                                         action='create',
                                         actor={'name': 'John Doe', 'id': 2},
                                         content={'name': 'Client Inc.',
                                                  'status': 'update',
                                                  'related': {
                                                      '_object': 'corporation',
                                                      'id': 'Gor Inc.'
                                                  },
                                                  'files': [2, 3],
                                                  'comments': ['Hello worlds']})
        hr1_data = HistoryRecordDiffSerializer(instance=hr1).data
        hr2_data = HistoryRecordDiffSerializer(instance=hr2).data
        diff = make_diff(hr1_data, hr2_data)
        awaited_diff = {
            'comments': {'insert': ['Hello worlds']},
            'status': {'update': 'update'},
            'related': {
                'update': {
                    '_object': 'corporation',
                    'id': 'Gor Inc.'
                }
            },
            'files': {
                'delete': [14],
                'insert': [3]
            }
        }
        assert diff == awaited_diff