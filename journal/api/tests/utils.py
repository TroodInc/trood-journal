from time import sleep

from journal.api.tests.factories import JournalFactory, HistoryRecordFactory


def _initialize_journal_data():
    journal = JournalFactory.create(alias='leads',
                                    name='Leads journal')
    hr1 = HistoryRecordFactory.create(journal=journal,
                                      type='clients',
                                      action='create',
                                      actor={'name': 'John Doe', 'id': 2},
                                      content={'name': 'Client Inc.',
                                               'status': 'new',
                                               'files': [1, 14]})

    sleep(3)

    hr2 = HistoryRecordFactory.create(journal=journal,
                                      type='clients',
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