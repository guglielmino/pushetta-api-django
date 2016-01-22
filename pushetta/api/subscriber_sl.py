# coding=utf-8

# Progetto: Pushetta API 
# Service layer con le funzionalità per la gestione Subscribers

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from core.models import Subscriber, Channel, ChannelSubscribeRequest
from core.models import ACCEPTED, PENDING

from api.serializers import SubscriberSerializer, ChannelSerializer, ChannelSubscribeRequestSerializer
from core.subscriber_manager import SubscriberManager


class SubscriberList(generics.GenericAPIView):
    """
    Handle device subscription to Pushetta
    """

    serializer_class = SubscriberSerializer

    def post(self, request, format=None):

        serializer = SubscriberSerializer(data=request.DATA)
        if serializer.is_valid():

            is_sandbox = (True if settings.ENVIRONMENT == "dev" else False)
            subscriber_data = serializer.object

            subscriber, created = Subscriber.objects.get_or_create(device_id=subscriber_data["device_id"],
                                                                   defaults={'sub_type': subscriber_data["sub_type"],
                                                                             'sandbox': is_sandbox, 'enabled': True,
                                                                             'name': subscriber_data["name"],
                                                                             'token': subscriber_data["token"]})

            if not created:
                subscriber.token = subscriber_data["token"]
                subscriber.name = subscriber_data["name"]

            subscriber.save()

            # Update del token nelle subscription del device
            subMamager = SubscriberManager()
            channel_subscriptions = subMamager.get_device_subscriptions(subscriber_data["device_id"])
            for channel_sub in channel_subscriptions:
                subMamager.subscribe(channel_sub, subscriber_data["sub_type"], subscriber_data["device_id"],
                                     subscriber_data["token"])

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubcriptionsList(generics.GenericAPIView):
    """
    Handle subscriptions to channels of a specific device
    """

    permission_classes = [
        permissions.AllowAny
    ]

    serializer_class = ChannelSerializer

    def get(self, request, format=None, deviceId=None):
        channel_names = SubscriberManager().get_device_subscriptions(deviceId)

        channels = Channel.objects.filter(name__in=channel_names)
        serializer = ChannelSerializer(channels, many=True)

        return Response(serializer.data)

      
class DeviceSubscriptionsRequests(generics.GenericAPIView):
    """
    Handle list of device requests (subscribed and pending subscriptions)
    """
    permission_classes = [
        permissions.AllowAny
    ]

    serializer_class = ChannelSubscribeRequestSerializer

    def get(self, request, format=None, deviceId=None):
        channel_names = SubscriberManager().get_device_subscriptions(deviceId)

        # Uso ChannelSubscribeRequestSerializer e quelli già sottoscritti li aggiungo fake come ACCEPTED
        channels = Channel.objects.filter(name__in=channel_names)
        subscribed = [ChannelSubscribeRequest(channel=ch, device_id=deviceId, status=ACCEPTED) for ch in channels]
        # Le richieste visualizzate client side sono solo quelle
        requests = ChannelSubscribeRequest.objects.filter(device_id=deviceId).filter(status=PENDING)

        serializer = ChannelSubscribeRequestSerializer(subscribed + list(requests), many=True)

        return Response(serializer.data)
