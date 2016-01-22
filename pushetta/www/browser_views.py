# coding=utf-8

# Progetto: Pushetta Site 
# Class view per la gestione dei metodi legati alla gestione delle push si Chrome

import json
import logging

logger = logging.getLogger(__name__)

from django.http import HttpResponse
from django.views.generic import View

from django.shortcuts import get_object_or_404

from core.services import ask_subscribe_channel

from core.models import Subscriber, Channel, User
from core.subscriber_manager import SubscriberManager


class WebPushRegistration(View):
    """
    Custom API to handle post of registration data (user, token,...)
    Invoked by Ajax call in callback of permissionRequest client side
    """
    
    
    
    # Check if device_id is subscriber of channel_name
    def get(self, request, device_id=None, channel_name=None):               
        channel = get_object_or_404(Channel, name=channel_name)

        channels = SubscriberManager().get_device_subscriptions(device_id)
        resp = 200
        if next((x for x in channels if x == channel.name.lower()), None) == None:
            resp = 404

        
        return HttpResponse(status=resp)

    # Subscribe to a channel
    def post(self, request):
        post_data = json.loads(request.body)
        channel_name = None
        if 'channel' in post_data:
            channel_name = post_data['channel']

        deviceToken = post_data['token']
        browser = post_data['browser']
        deviceId = post_data['device_id']
        
        name = "-"
        if request.user.is_authenticated():
            name = request.user.username

        # Create il subscriber if it doesn't exist
        subscriber, created = Subscriber.objects.update_or_create(device_id=deviceId,
                                                               defaults={'sub_type': browser,
                                                                         'sandbox': False, 'enabled': True,
                                                                         'name': name,
                                                                         'token': deviceToken})

        # Channel subscription
        if channel_name is not None:
            channel = get_object_or_404(Channel, name=channel_name)
            ask_subscribe_channel(channel, deviceId)

        return HttpResponse(status=201 if created else 200)

    # Delete a channel subscription
    def delete(self, request, device_id=None, channel_name=None):               
        channel = get_object_or_404(Channel, name=channel_name)
        channels = SubscriberManager().get_device_subscriptions(device_id)

        resp = 404
        if next((x for x in channels if x == channel.name.lower()), None) != None:
            current_dev = Subscriber.objects.get(device_id=device_id)
            SubscriberManager().unsubscribe(channel_name, device_id, current_dev.sub_type)
            resp = 200

        return HttpResponse(status=resp)
      

