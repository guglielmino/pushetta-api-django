# coding=utf-8

# Progetto: Pushetta Site 
# Class view per la gestione dei metodi legati alla gestione del token per le push su Safari

import os
import json
import logging

logger = logging.getLogger(__name__)

from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.conf import settings

from django.http import Http404
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from django.views.generic.edit import DeletionMixin
from django.views.generic.edit import CreateView
from django.template import RequestContext

from django.shortcuts import render_to_response, get_object_or_404
from django.core.files import File
from django.core.servers.basehttp import FileWrapper

from core.subscriber_manager import SubscriberManager
from core.services import ask_subscribe_channel, unsubscribe_channel, get_device_subscriptions

from core.models import Subscriber, ChannelSubscribeRequest, Channel
from core.models import ACCEPTED, REJECTED, PENDING, SUBSCRIBE_REQ_STATUS



class SafariPushService(View):
    """
    Handle token registration for Safari push
    """

    def post(self, request, deviceToken=None, websitePushID=None):
        logger.info("POST deviceToken={0} websitePushID={1}".format(deviceToken, websitePushID))
        return HttpResponse(status=200)

    def delete(self, request, deviceToken=None, websitePushID=None):
        logger.info("DELETE deviceToken={0} auth={1}".format(deviceToken, request.META['HTTP_AUTHORIZATION']))
        # Rimozione della subscription (a tendere valutare logical delete)
        # Subscriber.objects.filter(token=deviceToken).delete()
        subscribed_channels = get_device_subscriptions(deviceToken)

        for channel in [c.channel for c in subscribed_channels]:
            unsubscribe_channel(channel, deviceToken)

        return HttpResponse(status=200)


class SafariLogService(View):
    """
    Handle log of errors for Safari push
    """

    def post(self, request):
        logger.info("LOG BODY {0}".format(request.body))
        return HttpResponse(status=200)


class SafariPackageDownloadService(View):
    """
    Handle download of Website Package for Safari push notification
    """

    def post(self, request, deviceToken=None):
        PACKAGE_FILE = os.path.join(settings.BASE_DIR, '..', "var/Pushetta.pushpackage.zip")
        packageFile = open(PACKAGE_FILE, 'rb')

        response = HttpResponse(FileWrapper(packageFile), content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="%s"' % 'Pushetta.pushpackage.zip'
        return response
 