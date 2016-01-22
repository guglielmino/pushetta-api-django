# coding=utf-8

# Progetto: Pushetta API 
# Service layer con le funzionalità per feedback letture 

import logging
logger = logging.getLogger(__name__)

from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from api.serializers import FeedbackSerializer
from core.feedback_manager import FeedbackManager
from core.models import Channel
from api.permissions import IsDeviceCallAuthorized
from core.services import set_read_feedback_multiple


class FeedbackService(generics.GenericAPIView):
    serializer_class = FeedbackSerializer

    permission_classes = [
        IsDeviceCallAuthorized
    ]
    
    def post(self, request, format=None, messages_id=None):
        serializer = FeedbackSerializer(data=request.DATA)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
      
      
        feedback_dict = serializer.object
        set_read_feedback_multiple(feedback_dict["device_id"], feedback_dict["messages_id"])
        return Response(status=status.HTTP_201_CREATED)

      