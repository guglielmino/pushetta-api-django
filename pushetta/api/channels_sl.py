# coding=utf-8

# Progetto: Pushetta API 
# Service layer con le funzionalità per la gestione Channels

import logging

logger = logging.getLogger(__name__)

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, PageNotAnInteger
from haystack.query import SearchQuerySet
from haystack.inputs import Clean

from api.permissions import IsChannelOwner
from api.serializers import ChannelSerializer, ChannelSubscriptionSerializer, PaginatedChannelSerializer
from core.models import Channel, ChannelSubscribeRequest
from core.subscriber_manager import SubscriberManager

from core.services import ask_subscribe_channel, search_public_channels, get_suggested_channels
from core.services import SubscribeResponse


class ChannelsList(generics.ListCreateAPIView):
    """
    Class for handling Create/Update/List/Delete of Channels
    """
    model = Channel
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated, IsChannelOwner]

    def pre_save(self, obj):
        obj.owner = self.request.user

    def get_queryset(self):
        return Channel.objects.filter(owner=self.request.user)


class ChannelSearch(generics.ListAPIView):
    """
    Search for channels based on query keywords
    q -- keywords used in search 
    """

    model = Channel
    serializer_class = PaginatedChannelSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    def get(self, request, *args, **kwargs):
        q = request.QUERY_PARAMS.get('q', '')

        # sqs = SearchQuerySet().models(Channel).filter(content=Clean(q))
        sqs = search_public_channels(q)
        paginator = Paginator(sqs, 50)

        page = request.QUERY_PARAMS.get('page')
        if not page:
            page = 1
        try:
            channels = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page
            channels = paginator.page(1)
        except PageNotAnInteger:
            # If page is out of range, deliver last page
            channels = paginator.page(paginator.num_pages)

        serializer_context = {'request': request}
        serializer = PaginatedChannelSerializer(channels, context=serializer_context)
        return Response(serializer.data)


class ChannelSuggestion(generics.ListAPIView):
    """
    Channel suggestions based on popularity 
    """

    model = Channel
    serializer_class = ChannelSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    def get(self, request, device_id=None):
        suggestion = get_suggested_channels()
        if device_id is not None:
            # Vengono rimossi dai suggeriti quelli già sottoscritti
            channel_names = SubscriberManager().get_device_subscriptions(device_id)
            suggestion = [sugg for sugg in suggestion if not sugg.name.lower() in channel_names]

        serializer = ChannelSerializer(suggestion, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChannelSubscription(generics.GenericAPIView):
    """
    Handling of Channels subscriptions
    """
    serializer_class = ChannelSubscriptionSerializer

    permission_classes = [
        permissions.AllowAny
    ]

    def post(self, request, format=None, name=None):
        """
        Subscribe to the Channel identified by "name"
        """
        channels = Channel.objects.filter(name=name)
        if not channels:
            logger.error("Subscribe to inexistent channel : " + name)
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ChannelSubscriptionSerializer(data=request.DATA)
        if serializer.is_valid():
            subscriber_data = serializer.object
            channel = channels[0]
            subscribe_resp = ask_subscribe_channel(channel, subscriber_data['device_id'])

            if subscribe_resp == SubscribeResponse.SUBSCRIBED:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(status=(status.HTTP_202_ACCEPTED if subscribe_resp == SubscribeResponse.REQUEST_SEND
                                        else status.HTTP_400_BAD_REQUEST))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChannelUnSubscription(generics.GenericAPIView):
    """
    Handling of Channels subscriptions
    """
    serializer_class = ChannelSubscriptionSerializer

    permission_classes = [
        permissions.AllowAny
    ]


    # Nota: RFC2616 (http://www.w3.org/Protocols/rfc2616/rfc2616.html) definisce che è accettabile il DELETE con un body
    def delete(self, request, name=None, sub_type=None, device_id=None):
        """
        Unsubscribe from a channel
        """
        channels = Channel.objects.filter(name=name)
        if not channels:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not name is None and not device_id is None:
            result = status.HTTP_200_OK
            channel = channels[0]
            subManager = SubscriberManager()

            sub_token = subManager.get_subscription(channel.name, sub_type, device_id)
            if not sub_token is None:

                subManager.unsubscribe(channel.name, device_id, sub_type)

                # Dec num subscriptions
                channel.subscriptions = channel.subscriptions - 1
                channel.save()
            else:
                # Verifica che non si tratti di una subscription
                reqs = ChannelSubscribeRequest.objects.filter(device_id=device_id).filter(channel=channel)
                if reqs.count() > 0:
                    reqs[0].delete()
                else:
                    result = status.HTTP_404_NOT_FOUND

            return Response(status=result)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
