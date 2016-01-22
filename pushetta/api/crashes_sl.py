# coding=utf-8

# Progetto: Pushetta API 
# Service layer con le funzionalità per gestire i crashlog delle App (Android inizialmente)

from django.conf import settings
import logging

logger = logging.getLogger(__name__)

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status


class CrashLogService(generics.GenericAPIView):
    def post(self, request, format=None):
        logger.error(str(request.DATA))
        return Response(status=status.HTTP_200_OK)
      