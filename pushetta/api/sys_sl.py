# coding=utf-8

# Progetto: Pushetta API 
# Service layer con le API generiche di sistema (tipo check versione client) 

from datetime import datetime
from dateutil.relativedelta import relativedelta

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from api.permissions import IsChannelOwner

from api.serializers import CheckVersionSerializer

class CheckVersionData(object):
   def __init__(self, need_update, message):
      self.need_update = need_update
      self.message = message



class CheckVersion(generics.GenericAPIView):
    serializer_class = CheckVersionSerializer
    
    def get(self, request, *args, **kwargs):
       checkData = CheckVersionData(False, "")
       serializer = CheckVersionSerializer(checkData)
       return Response(serializer.data, status=status.HTTP_200_OK) 
