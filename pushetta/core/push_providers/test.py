# coding=utf-8

# Progetto: Pushetta API
# Test for push providers

import logging
logger = logging.getLogger(__name__)

from datetime import datetime
from datetime import timedelta

from django.test import TestCase
from django.conf import settings

from core.push_manager import PushProviderFactory
from core.push_providers.common import PushMessage, PushProviderException

class PushProvidersTestCase(TestCase):

    """
    Test cases for Push Providers
    """

    def setUp(self):
        settings.ENVIRONMENT = "dev"

    def test_ios_provider(self):
        # Creazione del messaggio da "pushare"
        extra_data = {"message_id": 141, "channel_name": "Test", "channel_image_url": "http://www.pushetta.com/uploads/channel_media/05e704fc35e544dfa50bacf89dda0eee.jpeg",
                  "ott": "111"}

        pmsg = PushMessage(alert_msg="Long text with ",
                       push_type="plain_push",
                       data_dic=extra_data)

        provider = PushProviderFactory.create('ios', logger)
        provider.pushMessage(pmsg, ['c0f5eb4db72a04d24d474e7cae5f1e7828f6f9bcaa8f083476e4840cc552a4c3'], "a channel")

    def test_mqtt_provider(self):
        extra_data = {
            "message_id": 141,
            "channel_name": "flower",
            "channel_image_url": "http://www.pushetta.com/uploads/channel_media/05e704fc35e544dfa50bacf89dda0eee.jpeg",
            "ott": "111"
        }


        pmsg = PushMessage(alert_msg="Message over MQTT test",
                       push_type="plain_push",
                       data_dic=extra_data)

        provider = PushProviderFactory.create('iot_device', logger)
        # Nota...il push su MQTT non richiede token perchè la subscription al canale è uno stato
        # persistente gestita dal protcollo (chi è connesso e ha fatto subscribe al topic riceve il messaggio)
        provider.pushMessage(pmsg, ['#'], "flower")


