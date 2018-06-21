import factory

from journal.api.models import Journal, HistoryRecord


class JournalFactory(factory.DjangoModelFactory):
    class Meta:
        model = Journal

    id = 'client'
    type = 'objects'
    target_key = 'id'
    actor_key = 'id'
    save_diff = True


class HistoryRecordFactory(factory.DjangoModelFactory):
    class Meta:
        model = HistoryRecord