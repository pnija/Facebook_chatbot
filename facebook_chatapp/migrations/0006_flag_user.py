# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-12-17 12:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('facebook_chatapp', '0005_flag'),
    ]

    operations = [
        migrations.AddField(
            model_name='flag',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='facebook_chatapp.Pizza'),
        ),
    ]
