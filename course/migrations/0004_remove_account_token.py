# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-14 08:23
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0003_auto_20181112_0744'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='token',
        ),
    ]
