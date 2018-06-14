from django.db import models


class Journal(models.Model):
    alias = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255, default='objects')
    history_record_key = models.CharField(max_length=255, default='pk')
    history_record_actor = models.CharField(max_length=255, default='actor.id')
    save_diff = models.BooleanField(default=True)
