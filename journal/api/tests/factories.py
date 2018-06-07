import factory

from journal.api.models import Journal, HistoryRecord


class JournalFactory(factory.DjangoModelFactory):
    class Meta:
        model = Journal

    alias = 'clients'
    type = 'objects'
    history_record_key = 'id'
    history_record_actor = 'actor.id'
    save_diff = True


class HistoryRecordFactory(factory.DjangoModelFactory):
    class Meta:
        model = HistoryRecord