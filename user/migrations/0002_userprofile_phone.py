# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-12-03 07:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='phone',
            field=models.CharField(default='', max_length=11, verbose_name='手机号'),
        ),
    ]
