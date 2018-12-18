# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Pizza(models.Model):

    pizza_type = models.TextField()
    size = models.TextField(null=True)
    crust = models.TextField(null=True)
    topping = models.TextField(null=True)
    extra = models.TextField(null=True)
    graph_location = models.CharField( max_length=128,null=True)
    address = models.CharField( max_length=128,null=True)
    user_id = models.IntegerField()


class Flag(models.Model):
    pickup_flag = models.IntegerField(null=True)
    delivery_flag = models.IntegerField(null =True)
    user = models.ForeignKey(Pizza, on_delete=models.CASCADE,null=True)