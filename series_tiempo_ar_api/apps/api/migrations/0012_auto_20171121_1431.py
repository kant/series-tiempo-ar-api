# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-21 19:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_catalog_identifier'),
    ]

    operations = [
        migrations.AlterField(
            model_name='field',
            name='series_id',
            field=models.CharField(max_length=200, unique=True),
        ),
    ]