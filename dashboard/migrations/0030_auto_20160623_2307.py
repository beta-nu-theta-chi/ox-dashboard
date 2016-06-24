# -*- coding: utf-8 -*-
# Generated by Django 1.10a1 on 2016-06-23 23:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0029_auto_20160623_2059'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chapterevent',
            old_name='date_time',
            new_name='start_datetime',
        ),
        migrations.RenameField(
            model_name='philanthropyevent',
            old_name='date_time',
            new_name='start_datetime',
        ),
        migrations.RenameField(
            model_name='recruitmentevent',
            old_name='date_time',
            new_name='start_datetime',
        ),
        migrations.RenameField(
            model_name='serviceevent',
            old_name='date_time',
            new_name='start_datetime',
        ),
        migrations.RemoveField(
            model_name='studytableevent',
            name='date',
        ),
        migrations.AddField(
            model_name='chapterevent',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='philanthropyevent',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='recruitmentevent',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='serviceevent',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studytableevent',
            name='end_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studytableevent',
            name='start_datetime',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]