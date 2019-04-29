# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-18 17:15
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20190303_0836'),
    ]

    operations = [
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('stripe_id', models.CharField(max_length=120)),
                ('paid', models.BooleanField(default=False)),
                ('refunded', models.BooleanField(default=False)),
                ('outcome', models.TextField(blank=True, null=True)),
                ('outcome_type', models.CharField(blank=True, max_length=120, null=True)),
                ('seller_message', models.CharField(blank=True, max_length=120, null=True)),
                ('risk_level', models.CharField(blank=True, max_length=120, null=True)),
            ],
        ),
        migrations.AlterField(
            model_name='order',
            name='date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 3, 18, 10, 15, 18, 24163)),
        ),
    ]
