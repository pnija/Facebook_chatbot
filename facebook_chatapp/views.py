# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re

from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sessions.models import Session
from facebook_chatbot.settings import TOKEN
from django.contrib.sessions.backends.db import SessionStore
from urllib3 import request
import datetime
from .models import *
import requests
import json
import ast


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
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token='+TOKEN
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
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token='+TOKEN
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)


# def unwanted(fbid):
#     pizza_obj = Pizza.objects.get(user_id=fbid)
#     if pizza_obj.pizza_type != ' ' and pizza_obj.size != ' ' and pizza_obj.address != ' ':
#         return '!delete'
#     else:
#         pizza_obj.delete()
#         return 'delete'


def pizza_type(fbid):
    type_pizza = "1.Prosciutto Pizza - 99 Rs(R),199 Rs(M),299 Rs(L),\n" \
                 "2.Cheese Pizza - 120 Rs(R),220 Rs(M),320 Rs(L),\n" \
                 "3.Buffalo Chicken Pizza - 110 Rs(R),210 Rs(M),310 Rs(L),\n" \
                 "4.Sweet Ricotta Pizza - 99 Rs(R),199 Rs(M),299 Rs(L),\n" \
                 "5.Brown Butter Pizza - 110 Rs(R),210 Rs(M),310 Rs(L),\n" \
                 "6.Grilled Zucchini Pizza - 120 Rs(R),220 Rs(M),320 Rs(L),\n" \
                 "7.Chicken Alfredo Pizza - 99 Rs(R),199 Rs(M),299 Rs(L)"
    received_message = type_pizza
    response_msg = json.dumps({"recipient": {"id": fbid},
                               "message": {"text": received_message, }
                               })
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token='+TOKEN
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
            now = str(datetime.datetime.now())
            now = now.split(' ')[0].split('-')
            session_obj = Session.objects.create(session_key=fbid,
                                                 expire_date=datetime.datetime(int(now[0]), int(now[1]), int(now[2]), 0,
                                                                               0, 20))
            session_obj.session_data = 1
            session_obj.save()
    if int(session_obj.session_data) == 1:
        if (value == 'pizza' and message[value][0]['confidence'] >= 0.6) or pizza_name_count >= 1:
            session_obj.session_data = 2

            session_obj.save()

            # response_msg = json.dumps({"recipient": {"id": fbid},
            #                            "message": {"text": "Which size you needed,Regular,Medium,Large", }
            #                            })
            pizza_list = ['prosciutto pizza', 'cheese pizza', 'buffalo chicken pizza', 'sweet ricotta pizza',
                          'brown butter pizza', 'grilled zucchini pizza', 'chicken alfredo pizza']
            pizza_price = {1: [99, 199, 299], 2: [120, 220, 320], 3: [110, 210, 310], 4: [99, 199, 299],
                           5: [110, 210, 310], 6: [120, 220, 320], 7: [99, 199, 299]}
            if pizza_name_count >= 1:
                pizza = pizza_list[int(received) - 1]
                pizza_obj = Pizza.objects.create(pizza_type=str(pizza), user_id=fbid)
                Price.objects.create(pizza_id=pizza_obj, pizza_price=str(pizza_price[int(received)]))
            else:
                received = received.lower()
                index_pizza = pizza_list.index(received)
                pizza_obj = Pizza.objects.create(pizza_type=received, user_id=fbid)
                Price.objects.create(pizza_id=pizza_obj, pizza_price=pizza_price[index_pizza+1])
            # pizza_obj = Pizza.objects.latest('id')
            pizza_name = pizza_obj.pizza_type
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": "You have selected " + pizza_name + "." + "\n,"
                                                            " Which size you needed,Regular,Medium,Large"}
                                       })
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
            size_list = ['regular', 'medium', 'large']
            received = received.lower()
            if received in size_list:
                pizza_obj = Pizza.objects.latest('id')
                pizza_obj.size = received
                pizza_obj.save()
                index_size =size_list.index(received)
                price_obj = Price.objects.get(pizza_id =pizza_obj)
                pizza_price_list = ast.literal_eval(price_obj.pizza_price)
                price_obj.one_pizza_price = pizza_price_list[index_size-1]
                price_obj.save()
                price_obj.size_index = index_size
                price_obj.save()
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": "Do you want to customize your pizza?", }
                                           })
            else:
                value = 'empty'
        if value != 'pizza' and value != 'pizza_size' and value != 'emptyy':
            value = 'empty'
        if value != 'emptyy':
            try:
                if message[value][0]['confidence'] < 0.6:
                    value = 'empty'
            except:
                value = 'empty'

    if int(session_obj.session_data) == 5:
        if (value == 'pizza_toppings' and message[value][0]['confidence'] >= 0.6) or pizza_name_count >= 1:
            if value == 'pizza_toppings' or value == 'eemptyy':
                session_obj.session_data = 6
                session_obj.save()
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": "Need any extra things,please specify?", }
                                           })
                topping_list = ["black olive", "onion", "crisp capsicum", "fresh tomato", "mushroom", "sausage",
                                "bbq chicken"]
                toppings_price = {1: [10, 20, 30], 2: [5, 10, 15], 3: [10, 20, 25], 4: [15, 20, 25], 5: [5, 10, 20],
                                    6: [10, 15, 20], 7: [5, 10, 15]}

                if pizza_name_count >= 1:

                    topping = topping_list[int(received) - 1]
                    pizza_obj = Pizza.objects.latest('id')
                    pizza_obj.topping = topping
                    pizza_obj.save()

                    price_obj = Price.objects.get(pizza_id=pizza_obj)
                    price_obj.toppings_price = toppings_price[int(received)]
                    price_obj.save()
                    price_obj.one_toppings_price = price_obj.toppings_price[price_obj.size_index]
                    price_obj.save()
                else:
                    received = received.lower()
                    pizza_obj = Pizza.objects.latest('id')
                    pizza_obj.topping = received
                    pizza_obj.save()
                    topping_list_index = topping_list.index(received)
                    price_obj = Price.objects.get(pizza_id=pizza_obj)
                    price_obj.toppings_price = toppings_price[topping_list_index + 1]
                    price_obj.save()
                    price_obj.one_toppings_price = price_obj.toppings_price[price_obj.size_index]
                    price_obj.save()
        if value != 'pizza_toppings' and value != 'pizza_crust_type' and value != 'eemptyy' and value != 'emptyy':
            value = 'empty'
            session_obj.session_data = int(session_obj.session_data) - 1
            session_obj.save()
        if value != 'eemptyy' and value != 'emptyy' and value != 'empty':
            if message[value][0]['confidence'] < 0.6:
                value = 'empty'
                session_obj.session_data = int(session_obj.session_data) - 1
                session_obj.save()

    if int(session_obj.session_data) == 4:
        flag_obj = Flag.objects.latest('id')
        if value == 'customization_no' and message[value][0]['confidence'] >= 0.6:
            session_obj.session_data = 5
            session_obj.save()
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": "Your order is cancelled", }
                                       })
            session_obj.session_data = 1
            session_obj.save()
        if value == 'customization_yes' and message[value][0]['confidence'] >= 0.6:
            session_obj.session_data = 4
            session_obj.save()
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": "Pickup or delivery", }
                                       })
        if (value == 'pizza_crust_type' and message[value][0]['confidence'] >= 0.6) or pizza_name_count >= 1:

            session_obj.session_data = 5
            session_obj.save()
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": "Select a topping,\n" \
                                                           " \n"\
                                                           "1.Black Olive - 10 Rs(R),20 Rs(M),30 Rs(L),\n" \
                                                           "2.Onion - 5 Rs(R),10 Rs(M),15 Rs(L),\n" \
                                                           "3.Crisp Capsicum - 10 Rs(R),20 Rs(M),25 Rs(L),\n" \
                                                           "4.Fresh Tomato - 15 Rs(R),20 Rs(M),25 Rs(L),\n" \
                                                           "5.Mushroom - 5 Rs(R),10 Rs(M),20 Rs(L),\n" \
                                                           "6.Sausage - 10 Rs(R),15 Rs(M),20 Rs(L),\n" \
                                                           "7.Bbq Chicken - 5 Rs(R),10 Rs(M),15 Rs(L)"}
                                       })

            crust_list = ["classic hand tossed", "wheat thin", "cheese burst", "fresh pan", "italian",
                          "cheese stuffed", "pizza bagels"]
            crust_price = {1: [10, 20, 30], 2: [15, 30, 45], 3: [20, 40, 50], 4: [15, 30, 45], 5: [10, 20, 30],
                           6: [20, 40, 50], 7: [20, 40, 50]}
            if pizza_name_count >= 1:

                crust = crust_list[int(received) - 1]
                pizza_obj = Pizza.objects.latest('id')
                pizza_obj.crust = crust
                pizza_obj.save()
                price_obj = Price.objects.get(pizza_id=pizza_obj)
                price_obj.crust_price = crust_price[int(received)]
                size_index = price_obj.size_index
                price_obj.save()
                crust_price_list = price_obj.crust_price
                price_obj.one_crust_price = crust_price_list[size_index]
                price_obj.save()
            else:
                received = received.lower()
                crust_list_index = crust_list.index(received)

                pizza_obj = Pizza.objects.latest('id')
                pizza_obj.crust = received
                pizza_obj.save()
                price_obj = Price.objects.get(pizza_id=pizza_obj)
                price_obj.crust_price = crust_price[crust_list_index+1]
                price_obj.save()
                size_index = price_obj.size_index
                price_obj.one_crust_price = price_obj.crust_price[size_index]
                price_obj.save()
        if (value != 'customization_no') and (value != 'pizza_crust_type') and (value != 'customization_yes') and (
                value != 'emptyy') and (value != 'pizza_toppings') and value != 'location':
            value = 'empty'
            session_obj.session_data = int(session_obj.session_data) - 1
            session_obj.save()
        if value != 'emptyy' and value != 'empty' and value != 'pizza_toppings':
            if message[value][0]['confidence'] < 0.6:
                value = 'empty'
                session_obj.session_data = int(session_obj.session_data) - 1
                session_obj.save()
    # pizza_customization crust

    if int(session_obj.session_data) == 3:
        pizza_obj = Pizza.objects.latest('id')
        price_obj = Price.objects.get(pizza_id=pizza_obj)
        if value == 'customization_no' and message[value][0]['confidence'] >= 0.6:
            session_obj.session_data = 4
            session_obj.save()
            price = str(price_obj.one_pizza_price)
            messages = "You have selected "+pizza_obj.pizza_type+" .The total pizza cost is " + price+"." +\
                       " Can I conform the order"
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": messages}
                                       })
        if value == 'customization_yes' and message[value][0]['confidence'] >= 0.6:
            session_obj.session_data = 4
            session_obj.save()
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": "Cool,pick a crust type,\n" \
                                                           " \n"\
                                                           "1.Classic Hand Tossed - 10 Rs(R),20 Rs(M),30 Rs(L),\n" \
                                                           "2.Wheat Thin - 15 Rs(R),30 Rs(M),45 Rs(L),\n" \
                                                           "3.Cheese Burst - 20 Rs(R),40 Rs(M),50 Rs(L),\n" \
                                                           "4.Fresh Pan - 15 Rs(R),30 Rs(M),45 Rs(L),\n" \
                                                           "5.Italian - 10 Rs(R),20 Rs(M),30 Rs(L),\n" \
                                                           "6.Cheese Stuffed - 20 Rs(R),40 Rs(M),50 Rs(L),\n" \
                                                           "7.Pizza Bagels - 20 Rs(R),40 Rs(M),50 Rs(L)"}
                                       })
        if ((value != 'customization_no') and (value != 'pizza_size') and (value != 'customization_yes')) or \
                message[value][0]['confidence'] < 0.6:
                value = 'empty'

    if int(session_obj.session_data) == 6:
        pizza_obj = Pizza.objects.latest('id')
        price_obj = Price.objects.get(pizza_id=pizza_obj)
        if (value != 'pizza_toppings') or message[value][0]['confidence'] < 0.6 or len(message) == 0:
            if value != 'eemptyy' and value != 'empty':
                session_obj.session_data = 7
                session_obj.save()
                price = str(price_obj.one_pizza_price+price_obj.one_crust_price+price_obj.one_toppings_price)

                messages = "You have selected "+pizza_obj.pizza_type+" with "+pizza_obj.crust+" crust and "\
                           +pizza_obj.topping+" topping .The total pizza cost is " + price + "." +\
                           " Can I conform the order ?"
                value = '!empty'
                pizza_obj = Pizza.objects.latest('id')
                pizza_obj.extra = received
                pizza_obj.save()
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": messages, }
                                           })

    if int(session_obj.session_data) == 7:
        if (value != 'pizza_toppings') or message[value][0]['confidence'] < 0.6 or len(message) == 0:
            if value == 'customization_yes' and message[value][0]['confidence'] >= 0.6:
                if value != 'eemptyy' and value != 'empty':
                    session_obj.session_data = 8
                    session_obj.save()
                    value = '!empty'
                    pizza_obj = Pizza.objects.latest('id')
                    pizza_obj.extra = received
                    pizza_obj.save()
                    response_msg = json.dumps({"recipient": {"id": fbid},
                                               "message": {"text": "Pickup or delivery", }
                                               })
            if value == 'customization_no' and message[value][0]['confidence'] >= 0.6:
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": "Your order is cancelled", }
                                           })
                session_obj.session_data = 1
                session_obj.save()
    if int(session_obj.session_data) == 8 or int(session_obj.session_data) == 4:
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
                session_obj.session_data = 9
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
            if value == 'pizza_toppings':
                value = 'empty'
    if int(session_obj.session_data) == 9:
        if value != '!empty':
            if value == 'location' or value == "email":
                session_obj.session_data = 10
                session_obj.save()
                pizza_obj = Pizza.objects.latest('id')
                pizza_obj.address = received
                pizza_obj.save()
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": "Please enter the mobile number"}
                                           })
            if value != 'pizza_toppings' and value != 'customization_no' and value != 'location' and value != "email":
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": "Please enter the information correctly"}
                                           })
    if int(session_obj.session_data) == 10:
        if value == "phone_number":
            mob_length = len(received)

            if mob_length == 10:
                session_obj.session_data = 11
                session_obj.save()
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {
                                               "text": "empty"}
                                           })
                flag_obj = Flag.objects.latest('id')
                if flag_obj.pickup_flag == 1:
                    response_msg = json.dumps({"recipient": {"id": fbid},
                                               "message": {
                                                   "text": "That's great!,"
                                                           "you can pick it after 30 min by paying cash directly."
                                                           "Thanks...visit again", }
                                               })
                if flag_obj.delivery_flag == 1:
                    response_msg = json.dumps({"recipient": {"id": fbid},
                                               "message": {
                                                   "text": "The pizza will be delivered within 1 hr,you can pay"
                                                           " cash on delivery."
                                                           "Thanks for your valuable time"}
                                               })


            else:
                response_msg = json.dumps({"recipient": {"id": fbid},
                                           "message": {"text": "Please enter a valid mobile number"}
                                           })
    if int(session_obj.session_data) == 11:
        if value != "phone_number":
            response_msg = json.dumps({"recipient": {"id": fbid},
                                       "message": {"text": " "}
                                       })
    if value == 'empty':
        response_msg = json.dumps({"recipient": {"id": fbid},
                                   "message": {"text": "sorry,I can't understand you"}
                                   })
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token='+TOKEN
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"}, data=response_msg)
