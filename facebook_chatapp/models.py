# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class User(models.Model):

    sender_id = models.IntegerField()

class Pizza(models.Model):

    pizza_type = models.TextField()
    size = models.TextField(null=True)
    crust = models.TextField(null=True)
    topping = models.TextField(null=True)
    extra = models.TextField(null=True)
    graph_location = models.CharField( max_length=128,null=True)
    address = models.CharField( max_length=128,null=True)
    user_id = models.IntegerField()
    user_id_id = models.ForeignKey(User, on_delete=models.CASCADE,null=True)