from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _
from django.db import models


class Journal(models.Model):
    owner = models.IntegerField(_('Owner'), null=True, default=None)
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, default='objects')
    target_key = models.CharField(max_length=255, default='id')
    actor_key = models.CharField(max_length=255, default='id')
    save_diff = models.BooleanField(default=True)


class HistoryRecordManager(models.Manager):
    def last_for_target(self, journal=None, target_id=None):
        if not (journal and target_id):
            return None

        prev_history_record = None

        records_content_not_null = journal.history_records.filter(
            content__isnull=False,
        )
        # Find previous history record
        if records_content_not_null.count() > 0:
            history_for_target = journal.history_records.filter(
                content__id=target_id
            )
            if history_for_target.count() > 0:
                prev_history_record = history_for_target.first()
        return prev_history_record


class HistoryRecord(models.Model):
    journal = models.ForeignKey(Journal, related_name='history_records')
    prev = models.ForeignKey('self', null=True)
    actor = JSONField()
    action = models.CharField(max_length=255)
    version = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    content = JSONField()
    diff = JSONField(null=True)
    objects = HistoryRecordManager()

    class Meta:
        ordering = ['-created_at']

    @property
    def revision(self):
        return self.prev
