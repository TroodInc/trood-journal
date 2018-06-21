# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-06-21 09:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20180621_0826'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='journal',
            name='history_record_actor',
        ),
        migrations.RemoveField(
            model_name='journal',
            name='history_record_key',
        ),
        migrations.AddField(
            model_name='journal',
            name='actor_key',
            field=models.CharField(default='id', max_length=255),
        ),
        migrations.AddField(
            model_name='journal',
            name='target_key',
            field=models.CharField(default='id', max_length=255),
        ),
    ]
