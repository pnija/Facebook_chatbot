# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from urllib3 import request
import datetime
from .models import *
import requests
import json


class YoMamaBotView(generic.View):

    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == '9745046321':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                if 'message' in message:
                    post_facebook_message(message['sender']['id'], message['message']['text'],
                                          message['message']['nlp']['entities'], request)
                    break
        return HttpResponse('')


def first_message(fbid, session_obj):
    session_obj.session_data = 1
    session_obj.save()
    received_message = 'Welcome to pizza hut. I am here to assist you to order pizza.You can select one from our menu'
    response_msg = json.dumps({"recipient": {"id": fbid},
                               "message": {"text": received_message, }
                               })
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAHUP2zu3sEBAITz6HfDWfukA8n' \
                       'TF8ziqwZC86RbgiZC5c9IZAr2m0GnBZBShwiuImZBYycIszE3ryN4gu6oRASff4RMJPUFVzwmlER1lE3awFIxKDV' \
                       'ZCu1yZAxYryxbWJ7zxJFAgnKSeG9rErTcjMDOTkEoDZBnQn8ndkJHhumCWUjz6WNOuWK6'
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def first_message_image(fbid):
    response_msg = json.dumps({"recipient": {"id": fbid},
                               "message": {
                                   "attachment": {

                                       "type": 'image',
                                       "payload": {
                                           "url": "http://www.talkingtrendo.com/wp-content/uploads/2013/01/dominos-"
                                                  "menu-price21.jpg",
                                       },
                                   },
                               }
                               })
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAHUP2zu3sEBAITz6HfDWfukA8nTF8ziqw' \
                       'ZC86RbgiZC5c9IZAr2m0GnBZBShwiuImZBYycIszE3ryN4gu6oRASff4RMJPUFVzwmlER1lE3awFIxKDVZCu1yZAxYry' \
                       'xbWJ7zxJFAgnKSeG9rErTcjMDOTkEoDZBnQn8ndkJHhumCWUjz6WNOuWK6'
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def pizza_type(fbid):
    type_pizza = "1.Prosciutto Pizza,\n" \
                 "2.Cheese Pizza,\n" \
                 "3.Buffalo Chicken Pizza,\n" \
                 "4.Sweet Ricotta Pizza,\n" \
                 "5.Brown Butter Pizza,\n" \
                 "6.Grilled Zucchini Pizza,\n" \
                 "7.Chicken Alfredo Pizza"
    received_message = type_pizza
    response_msg = json.dumps({"recipient": {"id": fbid},
                               "message": {"text": received_message, }
                               })
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAHUP2zu3sEBAITz6HfDWfukA8nTF8' \
                       'ziqwZC86RbgiZC5c9IZAr2m0GnBZBShwiuImZBYycIszE3ryN4gu6oRASff4RMJPUFVzwmlER1lE3awFIxKDVZCu1yZA' \
                       'xYryxbWJ7zxJFAgnKSeG9rErTcjMDOTkEoDZBnQn8ndkJHhumCWUjz6WNOuWK6'
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


def post_facebook_message(fbid, received, message, request):
    # session_obj = Session.objects.create(pk=fbid)
    try:
        session_obj = Session.objects.get(session_key=fbid)
    except:
        session_obj = Session.objects.create(session_key=fbid, expire_date=datetime.datetime(2018, 12, 16))
    try:
        if int(session_obj.session_data) >= 0:
            pass
    except:
        session_obj.session_data = 0
        session_obj.save()
    value = 'empty'
    intent_list = []
    confidence_list = []
    intents = ['greetings', 'pizza_intent', 'pizza', 'pizza_size', 'customization_no', 'customization_yes',
               'pizza_crust_type', 'location', 'phone_number', 'email']
    for type in message:
        intent_list.append(type)

    for conf_val in intent_list:
        confidence_list.append(message[conf_val][0]['confidence'])
    if confidence_list:
        max_confidence = max(confidence_list)
        index = confidence_list.index(max_confidence)
        value = intent_list[index]
    if ('pizza_intent' or 'pizza') in intent_list:
        value = 'pizza'
    if (value == 'greetings' or value == 'pizza_intent') and message[value][0]['confidence'] >= 0.6:
        first_message(fbid, session_obj)
        first_message_image(fbid)
        pizza_type(fbid)
        response_msg = json.dumps({"recipient": {"id": fbid},
                                   "message": {"text": ' ', }
                                   })
    pizza_name_count = 0
    # if user select number
    if received in ['1', '2', '3', '4', '5', '6', '7']:
        pizza_name_count = received
        value = 'emptyy'
        if int(session_obj.session_data) == 5:
            value = 'eemptyy'
    x = session_obj.session_data
    if int(session_obj.session_data) > 0:
        if (value == 'greetings' or value == 'pizza_intent') and message[value][0]['confidence'] >= 0.6:
            session_obj.delete()
            session_obj = Session.objects.create(session_key=fbid, expire_date=datetime.datetime(2018, 12, 20))
            session_obj.session_data = 1
            session_obj.save()
    if int(session_obj.session_data) == 1:
        if (value == 'pizza' and message[value][0]['confidence'] >= 0.6) or pizza_name_count >= 1:
            session_obj.session_data = 2

            session_obj.save()

            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": "Which size you needed,Regular,Medium,Large", }
                                       })
            pizza_list = ['prosciutto pizza', 'cheese pizza', 'buffalo chicken pizza', 'sweet ricotta pizza',
                          'brown butter pizza', 'grilled zucchini pizza', 'chicken alfredo pizza']
            if pizza_name_count >= 1:
                pizza = pizza_list[int(received) - 1]
                Pizza.objects.create(pizza_type=str(pizza), user_id=fbid)
            else:
                received = received.lower()
                pizza_obj = Pizza.objects.create(pizza_type=received, user_id=fbid)
        if value != 'pizza' and value != 'greetings' and value != 'emptyy':
            value = 'empty'
        if value != 'emptyy' and value != 'empty':
            if message[value][0]['confidence'] < 0.6:
                value = 'empty'
    # handle pizza size

    if int(session_obj.session_data) == 2:

        if value == 'pizza_size' and message[value][0]['confidence'] >= 0.6:
            session_obj.session_data = 3
            session_obj.save()
            pizza_obj = Pizza.objects.latest('id')
            pizza_obj.size = received
            pizza_obj.save()
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": "Do you want to customize your pizza?", }
                                       })
        if value != 'pizza' and value != 'pizza_size' and value != 'emptyy':
            value = 'empty'
        if value != 'emptyy':
            try:
                if message[value][0]['confidence'] < 0.6:
                    value = 'empty'
            except:
                value = 'empty'
    # pizza_customization crust

    if int(session_obj.session_data) == 3:
        if value == 'customization_no' and message[value][0]['confidence'] >= 0.6:
            session_obj.session_data = 4
            session_obj.save()
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": "Pickup or delivery", }
                                       })
        if value == 'customization_yes' and message[value][0]['confidence'] >= 0.6:
            session_obj.session_data = 4
            session_obj.save()
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": "Cool,pick a crust type,\n" \
                                                           "1.Classic Hand Tossed,\n" \
                                                           "2.Wheat Thin Crust,\n" \
                                                           "3.Cheese Burst,\n" \
                                                           "4.Fresh Pan,\n" \
                                                           "5.Italian Crust"}
                                       })
        if ((value != 'customization_no') and (value != 'pizza_size') and (value != 'customization_yes')) or \
                message[value][0]['confidence'] < 0.6:
            value = 'empty'
    # pizza_customization toppings
    if int(session_obj.session_data) == 4:
        if (value == 'pizza_crust_type' and message[value][0]['confidence'] >= 0.6) or pizza_name_count >= 1:
            session_obj.session_data = 5
            session_obj.save()
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": "Select a topping,\n" \
                                                           "1.Black Olive,\n" \
                                                           "2.Onion,\n" \
                                                           "3.Crisp Capsicum,\n" \
                                                           "4.Fresh Tomato,\n" \
                                                           "5.Mushroom,\n" \
                                                           "6.Bbq Chicken"}
                                       })

            crust_list = ["classic hand tossed", "wheat thin crust", "cheese burst", "fresh pan", "italian crust"]
            if pizza_name_count >= 1:

                crust = crust_list[int(received) - 1]
                pizza_obj = Pizza.objects.latest('id')
                pizza_obj.crust = crust
                pizza_obj.save()
            else:
                received = received.lower()
                pizza_obj = Pizza.objects.latest('id')
                pizza_obj.crust = received
                pizza_obj.save()
        if (value != 'customization_no') and (value != 'pizza_crust_type') and (value != 'customization_yes') and (
                value != 'emptyy') and (value != 'pizza_toppings'):
            value = 'empty'
            session_obj.session_data = int(session_obj.session_data) - 1
            session_obj.save()
        if value != 'emptyy' and value != 'empty' and value != 'pizza_toppings':
            if message[value][0]['confidence'] < 0.6:
                value = 'empty'
                session_obj.session_data = int(session_obj.session_data) - 1
                session_obj.save()
    if int(session_obj.session_data) == 5:
        if (value == 'pizza_toppings' and message[value][0]['confidence'] >= 0.6) or pizza_name_count >= 1:
            if value == 'pizza_toppings' or value == 'eemptyy':
                session_obj.session_data = 6
                session_obj.save()
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": "Need any extra things,please specify?", }
                                           })
                topping_list = ["classic hand tossed", "wheat thin crust", "cheese burst", "fresh pan", "italian crust"]

                if pizza_name_count >= 1:

                    topping = topping_list[int(received) - 1]
                    pizza_obj = Pizza.objects.latest('id')
                    pizza_obj.topping = topping
                    pizza_obj.save()
                else:
                    received = received.lower()
                    pizza_obj = Pizza.objects.latest('id')
                    pizza_obj.topping = received
                    pizza_obj.save()
        if value != 'pizza_toppings' and value != 'pizza_crust_type' and value != 'eemptyy' and value != 'emptyy':
            value = 'empty'
            session_obj.session_data = int(session_obj.session_data) - 1
            session_obj.save()
        if value != 'eemptyy' and value != 'emptyy' and value != 'empty':
            if message[value][0]['confidence'] < 0.6:
                value = 'empty'
                session_obj.session_data = int(session_obj.session_data) - 1
                session_obj.save()
    if int(session_obj.session_data) == 6:
        if (value != 'pizza_toppings') or message[value][0]['confidence'] < 0.6 or len(message) == 0:
            if value != 'eemptyy' and value != 'empty':
                session_obj.session_data = 7
                session_obj.save()
                value = '!empty'
                pizza_obj = Pizza.objects.latest('id')
                pizza_obj.extra = received
                pizza_obj.save()
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": "Pickup or delivery", }
                                           })

    if int(session_obj.session_data) == 7 or int(session_obj.session_data) == 4:
        if (value != 'customization_no' and value != 'customization_yes') or value == 'pizza_toppings':
            flag = 0
            received = received.lower()
            received_list = received.split(' ')
            for i in received_list:
                for j in ['pickup', 'delivery']:
                    if i == j:
                        flag = 1
                        received = i
            if value != 'empty' and value != '!empty':
                if message[value][0]['confidence'] > 0.6:
                    value = "empty"
            if flag == 1:
                session_obj.session_data = 8
                session_obj.save()
                flag_obj = Flag.objects.all()
                if received == "pickup":
                    pizza_obj = Pizza.objects.latest('id')
                    Flag.objects.create(user=pizza_obj, pickup_flag=1)
                    value = '!empty'
                    response_msg = json.dumps({"recipient": {"id": fbid},
                                               "message": {"text": "Please enter your email", }
                                               })
                if received == "delivery":
                    pizza_obj = Pizza.objects.latest('id')
                    Flag.objects.create(user=pizza_obj, delivery_flag=1)
                    value = '!empty'
                    response_msg = json.dumps({"recipient": {"id": fbid},
                                               "message": {"text": "Enter the your name and address"}
                                               })
    if int(session_obj.session_data) == 8:
        if value != '!empty':
            if value == 'location' or value == "email":
                session_obj.session_data = 9
                session_obj.save()
                pizza_obj = Pizza.objects.latest('id')
                pizza_obj.address = received
                pizza_obj.save()
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": "please enter the mobile number"}
                                           })
            if value != 'pizza_toppings' and value != 'customization_no' and value != 'location' and value != "email":
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": "Please enter the information correctly"}
                                           })
    if int(session_obj.session_data) == 9:
        if value == "phone_number":
            mob_length = len(received)

            if mob_length == 10:
                session_obj.session_data = 10
                session_obj.save()
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {
                                               "text": "empty"}
                                           })
                flag_obj = Flag.objects.latest('id')
                if flag_obj.pickup_flag == 1:
                    response_msg = json.dumps({"recipient": {"id": fbid},
                                               "message": {
                                                   "text": "That's great!,the total pizza cost is 250 rs."
                                                           "You can pick it after 30 min by paying cash directly."
                                                           "Thanks...visit again", }
                                               })
                if flag_obj.delivery_flag == 1:
                    response_msg = json.dumps({"recipient": {"id": fbid},
                                               "message": {
                                                   "text": "The total pizza cost is 250 and you can pay cash "
                                                           "on delivery .The pizza will be delivered within 1 hr."
                                                           "Thanks for your valuable time"}
                                               })
            else:
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": "Please enter a valid mobile number"}
                                           })
    if int(session_obj.session_data) == 10:
        if value != "phone_number":
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": " "}
                                       })
    if value == 'empty':
        response_msg = json.dumps({"recipient": {"id": fbid},
                                   "message": {"text": "sorry,I can't understand you"}
                                   })
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAHUP2zu3sEBAITz6HfDWfukA8nTF8ziqwZ' \
                       'C86RbgiZC5c9IZAr2m0GnBZBShwiuImZBYycIszE3ryN4gu6oRASff4RMJPUFVzwmlER1lE3awFIxKDVZCu1yZAxYry' \
                       'xbWJ7zxJFAgnKSeG9rErTcjMDOTkEoDZBnQn8ndkJHhumCWUjz6WNOuWK6'
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
