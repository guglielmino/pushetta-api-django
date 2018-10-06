# coding=utf-8

# Progetto: Pushetta API
# Provider for push to Apple Push Message System

import logging
import sys
import traceback
import random

from django.conf import settings
import time

from common import BaseProvider
from apns import APNs, Frame, Payload


# Doc per implementazione qui https://github.com/djacobs/PyAPNs
# Nota installare con "pip install git+git://github.com/djacobs/PyAPNs.git"


#  Procedura di invio massivo ispirata a https://gist.github.com/jimhorng/594401f68ce48282ced5
SEND_INTERNAL = 0.01


class iOSPushProvider(BaseProvider):

    def response_listener(self, error_response):
        self.log_info(
            "iOSprovider:client get error-response: " + str(error_response))

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
                self.apns = APNs(use_sandbox=settings.APNS_IS_SANDBOX,
                                 cert_file=settings.APNS_CERT_FILE, enhanced=True)

                payload = Payload(
                    alert=message.alert_msg, sound="notification.aiff", badge=1, custom=message.data_dic)

                # TODO: Gestire l'expire
                # Expire in un mese di default (TODO: Ricavare dai dati passati)
                expiry = time.time() + 3600 * 24 * 30

                priority = 10
                for token in destToken:
                    self.log_info(
                        "iOSPushProvider -- send token {0}".format(token))
                    identifier = random.getrandbits(32)
                    self.apns.gateway_server.register_response_listener(
                        self.response_listener)
                    self.apns.gateway_server.send_notification(
                        token, payload, identifier=identifier)

                # Get feedback messages.
                for (token_hex, fail_time) in self.apns.feedback_server.items():
                    self.log_info(
                        "iOSPushProvider -- feedback token {0} fail time {1}".format(token_hex, fail_time))
                delay = self.wait_till_error_response_unchanged()
                self.apns.gateway_server.force_close()
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                lines = traceback.format_exception(
                    exc_type, exc_value, exc_traceback)
                self.log_error(
                    "iOSPushProvider -- exception {0}".format(''.join('!! ' + line for line in lines)))
        else:
            self.log_info("Nothing to send for iOSPushProvider")

        return send_count
