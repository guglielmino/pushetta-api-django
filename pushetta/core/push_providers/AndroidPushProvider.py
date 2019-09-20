# coding=utf-8

# Progetto: Pushetta API 
# Provider for push to Google Cloud Messaging

import logging

import sys
import traceback
import random
from pyfcm import FCMNotification
from django.conf import settings

from common import BaseProvider

# Samples for FCM pip module here https://github.com/olucurious/pyfcm

class AndroidPushProvider(BaseProvider):
    def __init__(self):
        self.gcm = FCMNotification(api_key=settings.FCM_SERVER_KEY)


    def pushMessage(self, message, destToken, channel_name):
        send_count = len(destToken)

        if send_count > 0:
            # TODO: Gestire paginazione dei tokens a gruppi di 6/700 (il limite dovrebbe essere 1000 per call)
            # TODO: gestione del ttl
            # Nota: converto in un dict perché altrimenti il serializzatore non riesce a lavorare sul PushMessage
            dic_obj = {'alert_msg': message.alert_msg, 'data_dic': message.data_dic, 'push_type': message.push_type}
            response = self.gcm.notify_multiple_devices(registration_ids=destToken, message_body=message.alert_msg, data_message=dic_obj)

            self.log_debug(str(response))

            # Handling errors
            if 'errors' in response:
                for error, reg_ids in response['errors'].items():
                    self.log_error("push error {0}".format(error))
                    # Check for errors and act accordingly
                    if error is 'NotRegistered':
                        pass
                        # Remove reg_ids from database
                        # for reg_id in reg_ids:
                        # entity.filter(registration_id=reg_id).delete()

            if 'canonical' in response:
                for reg_id, canonical_id in response['canonical'].items():
                    self.log_error("canonical {0}".format(reg_id))
                    # # Repace reg_id with canonical_id in your database
                    # entry = entity.filter(registration_id=reg_id)
                    #      entry.registration_id = canonical_id
                    #      entry.save()

            # Nota: al momento non viene gestito correttamente il conteggio dei push inviati, si da per scontato che tutti
            # lo siano
        else:
            self.log_info("Nothing to send for AndroidPushProvider")


        return send_count