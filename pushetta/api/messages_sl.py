# coding=utf-8

# Progetto: Pushetta API 
# Service layer con le funzionalità dei messaggi storati 

from datetime import datetime

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Q

from api.serializers import ChannelMsgSerializer
from core.subscriber_manager import SubscriberManager
from core.models import ChannelMsg
from api.permissions import IsDeviceCallAuthorized


class MessageList(generics.GenericAPIView):
    """
    Get a single message or a messages list belonging to
    calling device
    message_id -- Message identifier
    """

    serializer_class = ChannelMsgSerializer

    permission_classes = [
        IsDeviceCallAuthorized
    ]

    # NOTA: Va definito un meccanismo di protezione per la get dei messaggi di un device per evitare
    # che conoscendo il device_id di un utente si possano acquisire i messaggi (problema reale solo
    #       per i canali privati, quelli pubblici hanno messaggi visibili a tutti per definizione)
    def get(self, request, format=None, message_id=None, device_id=None):

        if message_id != None:
            obj = get_object_or_404(ChannelMsg, pk=message_id)
            serializer = ChannelMsgSerializer(obj)

            return Response(serializer.data, status=status.HTTP_200_OK)

        if device_id != None:
            channel_names = SubscriberManager().get_device_subscriptions(device_id)
            # Nota: verificare come gestire la casistica di risultati molto ampi, introdotto inanto il throttling per limitare
            messages = ChannelMsg.objects.filter(Q(expire__isnull=True) | Q(expire__gte=datetime.utcnow())).filter(
                channel__name__in=channel_names)
            serializer = ChannelMsgSerializer(messages, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(status=status.HTTP_404_NOT_FOUND)
         
