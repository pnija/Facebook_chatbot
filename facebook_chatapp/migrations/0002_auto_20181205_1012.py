# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-05 10:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_chatapp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pizza',
            name='address',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='pizza',
            name='extra',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='pizza',
            name='graph_location',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AlterField(
            model_name='pizza',
            name='size',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='pizza',
            name='topping',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='pizza',
            name='user_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='facebook_chatapp.User'),
        ),
    ]
