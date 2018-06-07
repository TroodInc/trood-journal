from django.contrib.postgres.fields import JSONField
from django.db import models


class Journal(models.Model):
    alias = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, default='objects')
    history_record_key = models.CharField(max_length=255, default='pk')
    history_record_actor = models.CharField(max_length=255, default='actor.id')
    save_diff = models.BooleanField(default=True)


class HistoryRecord(models.Model):
    journal = models.ForeignKey(Journal, related_name='history_records')
    actor = JSONField()
    action = models.CharField(max_length=255)
    version = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    content = JSONField()
    diff = JSONField(null=True)

    class Meta:
        ordering = ['-created_at']
