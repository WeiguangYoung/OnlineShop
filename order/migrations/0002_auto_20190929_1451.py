# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-09-29 06:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderinfo',
            name='status',
            field=models.SmallIntegerField(choices=[(1, '待付款'), (2, '待发货'), (3, '待收货')], verbose_name='订单状态'),
        ),
    ]
