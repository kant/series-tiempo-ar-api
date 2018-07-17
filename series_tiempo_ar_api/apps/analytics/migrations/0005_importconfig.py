# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2018-06-07 19:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analytics', '0004_auto_20180117_1045'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('endpoint', models.URLField()),
                ('token', models.CharField(max_length=64)),
                ('kong_api_id', models.CharField(max_length=64)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]