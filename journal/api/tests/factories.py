import factory

from journal.api.models import Journal


class JournalFactory(factory.DjangoModelFactory):
    class Meta:
        model = Journal

    type = 'objects'
    history_record_key = 'id'
    history_record_actor = 'actor.id'
    save_diff = True