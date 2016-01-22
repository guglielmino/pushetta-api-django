# coding=utf-8

# Progetto: Pushetta API 
# push provider for Safari browser push notification

import logging
import sys
import traceback
import random

from django.conf import settings
import time

from common import BaseProvider
from apns import APNs, Frame, Payload
from common import PushMessage, BaseProvider, PushProviderException

#  Procedura di invio massivo ispirata a https://gist.github.com/jimhorng/594401f68ce48282ced5
SEND_INTERNAL = 0.01

# Custom payload class fr Safari
class PayloadSafari(Payload):
 
    def __init__(self, alert=None, url_args=[]):
        super(Payload, self).__init__()
        self.alert = alert
        self.url_args = url_args
        self._check_size()
 
    def dict(self):
        d = {"alert": self.alert, "url-args": self.url_args}
        d = {'aps': d}
        #print d
        return d
        
        
class SafariPushProvider(BaseProvider):

    def response_listener(self, error_response):
        self.log_info("client get error-response: " + str(error_response))

    def wait_till_error_response_unchanged(self):

        if hasattr(self.apns.gateway_server, '_is_resending'):
            delay = 1
            count = 0
            while True:
                if self.apns.gateway_server._is_resending == False:
                    time.sleep(delay)
                    if self.apns.gateway_server._is_resending == False:
                        count = count + delay
                    else:
                        count = 0
                else:
                    count = 0

                if count >= 10:
                    break
            return delay * count
        return 0

    def pushMessage(self, message, destToken, channel_name):
        send_count = len(destToken)
        if send_count > 0:
            try:
                # USO l'apns enanched
                self.apns = APNs(use_sandbox=settings.APNS_IS_SANDBOX, cert_file=settings.APNS_SAFARI_CERT_FILE, enhanced=True)

                alert_dict = {"title": message.alert_msg[:40], "body": message.alert_msg, "action": "View"}
                payload = PayloadSafari(alert=alert_dict, url_args = [message.data_dic['channel_name']])

                # TODO: Gestire l'expire
                expiry = time.time() + 3600 * 24 * 30  # Expire in un mese di default (TODO: Ricavare dai dati passati)

                priority = 10
                for token in destToken:
                    self.log_info("SafariPushProvider -- send token {0}".format(token))
                    identifier = random.getrandbits(32)
                    self.apns.gateway_server.register_response_listener(self.response_listener)
                    self.apns.gateway_server.send_notification(token, payload, identifier=identifier)

                # Get feedback messages.
                for (token_hex, fail_time) in self.apns.feedback_server.items():
                    self.log_info("SafariPushProvider -- feedback token {0} fail time {1}".format(token_hex, fail_time))
                delay = self.wait_till_error_response_unchanged()
                self.apns.gateway_server.force_close()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
                self.log_error("SafariPushProvider -- exception {0}".format(''.join('!! ' + line for line in lines)))
        else:
            self.log_info("Nothing to send for SafariPushProvider")


        return send_count

