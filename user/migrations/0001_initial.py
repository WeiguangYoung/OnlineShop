# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-09-24 04:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('receiver', models.CharField(max_length=10, verbose_name='收件人')),
                ('address', models.CharField(max_length=100, verbose_name='用户地址')),
                ('default_address', models.BooleanField(verbose_name='默认地址')),
                ('is_alive', models.BooleanField(default=True, verbose_name='是否删除')),
                ('postcode', models.CharField(max_length=7, verbose_name='邮政编码')),
                ('receiver_mobile', models.CharField(max_length=11, verbose_name='电话')),
                ('tag', models.CharField(default=None, max_length=10, verbose_name='标签')),
            ],
            options={
                'db_table': 'address',
                'verbose_name_plural': '用户地址',
                'verbose_name': '用户地址',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=11, unique=True, verbose_name='用户名')),
                ('password', models.CharField(max_length=32)),
                ('email', models.CharField(max_length=50, verbose_name='邮箱')),
                ('phone', models.CharField(max_length=11, verbose_name='手机')),
                ('isActive', models.BooleanField(default=False, verbose_name='激活状态')),
            ],
            options={
                'db_table': 'user_profile',
            },
        ),
        migrations.CreateModel(
            name='WeiboUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('weibo_token', models.CharField(max_length=40, verbose_name='微博token')),
                ('uid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.UserProfile', verbose_name='用户id')),
            ],
            options={
                'db_table': 'weibouser',
                'verbose_name_plural': '微博用户表',
                'verbose_name': '微博用户表',
            },
        ),
        migrations.AddField(
            model_name='address',
            name='uid',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='address', to='user.UserProfile', verbose_name='用户id'),
        ),
    ]
