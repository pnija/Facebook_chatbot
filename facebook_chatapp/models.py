# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Pizza(models.Model):

    pizza_type = models.TextField()
    size = models.TextField(null=True)
    crust = models.TextField(null=True)
    topping = models.TextField(null=True)
    extra = models.TextField(null=True)
    graph_location = models.CharField( max_length=128, null=True)
    address = models.CharField(max_length=128, null=True)
    user_id = models.IntegerField()


class Flag(models.Model):
    pickup_flag = models.IntegerField(null=True)
    delivery_flag = models.IntegerField(null=True)
    user = models.ForeignKey(Pizza, on_delete=models.CASCADE, null=True)


class Price(models.Model):
    pizza_price = models.CharField(max_length=20, null=True)
    crust_price = models.CharField(max_length=20, null=True)
    toppings_price = models.CharField(max_length=20, null=True)
    one_pizza_price = models.IntegerField(blank=True, null=True)
    one_crust_price = models.IntegerField(blank=True, null=True)
    one_toppings_price = models.IntegerField(blank=True, null=True)
    size_index = models.IntegerField(blank=True, null=True)
    pizza_id = models.ForeignKey(Pizza, on_delete=models.CASCADE, null=True)

