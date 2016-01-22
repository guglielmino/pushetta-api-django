# coding=utf-8

# Progetto: Pushetta API 
# Service layer con le funzionalità di push e lettura dei messaggi 

from datetime import datetime
from dateutil.relativedelta import relativedelta

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import UserRateThrottle

from django.conf import settings

from core.models import Channel, ChannelMsg
from api.serializers import PushMessageSerializer, PushResponseSerializer, TargetSerializer

from core.services import send_push_message, get_push_targets, SendPushResponse

class PushList(generics.GenericAPIView):
    serializer_class = PushMessageSerializer
    throttle_classes = (UserRateThrottle,)
    
    #permission_classes = (IsChannelOwner, permissions.IsAuthenticated,)

    def post(self, request, format=None, name=None):
        channel = None
        try:
            channel = Channel.objects.get(name=name)
        except Channel.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if channel.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)

        serializer = PushMessageSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        push_msg = serializer.object

        expire = datetime.today() + relativedelta(months=1) # Default 1 mese
        if 'expire' in push_msg:
            expire = push_msg["expire"]

        target = None
        if "target" in push_msg:
            target = push_msg["target"]
          
        response = send_push_message(channel, push_msg["message_type"], push_msg["body"], expire, target)

        serializer = PushResponseSerializer(response)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TargetList(generics.GenericAPIView):
    serializer_class = TargetSerializer

    def get(self, request):
        resp_list = map(lambda x: { "target" : x}, get_push_targets())
        serializer = TargetSerializer(resp_list)
        return Response(serializer.source, status=status.HTTP_200_OK)