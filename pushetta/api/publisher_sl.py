# coding=utf-8

# Progetto: Pushetta API 
# Service layer con le funzionalità per la gestione Publishers

from rest_framework import generics

from api.serializers import PublisherSerializer




class PublisherList(generics.GenericAPIView):
    """
    Channels publishers subscriptions
    """
    serializer_class = PublisherSerializer

    def post(self, request, format=None, name=None):
        pass