# coding=utf-8

# Progetto: Pushetta API 
# Push provider for MQTT protocol

import sys
import traceback
import random
from common import PushMessage, BaseProvider, PushProviderException
import paho.mqtt.publish as publish
from django.conf import settings

class MQTTPushProvider(BaseProvider):
    push_pattern = "/pushetta.com/channels/{0}"

    def pushMessage(self, message, tokens, channel_name):
        if not isinstance(tokens, list):
            raise PushProviderException("tokens must be a list")
            return False

        if not isinstance(message, PushMessage):
            raise PushProviderException("message must be a PushMessage")
            return False

        # TODO: Condizionare il push verso MQTT al message.push_type ??

        try:
            topic = self.push_pattern.format(channel_name)
            auth_object = {'username': settings.MOSQ_USERNAME, 'password': settings.MOSQ_PASSWORD}
            publish.single(topic, payload=message.alert_msg, qos=1, retain=False, hostname=settings.MOSQ_HOST,
                           port=settings.MOSQ_PORT, client_id="pushetta-api", keepalive=60, auth=auth_object)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
            self.log_error("MQTTPushProvider -- exception {0}".format(''.join('!! ' + line for line in lines)))

        return True