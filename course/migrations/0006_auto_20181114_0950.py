# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-14 09:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0005_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='create_time',
            field=models.CharField(max_length=128),
        ),
    ]