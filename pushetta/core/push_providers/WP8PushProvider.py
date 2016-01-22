# coding=utf-8

# Progetto: Pushetta API 
# Provider for push to Windows Phone 8 Platform

import logging

from mpns import MPNSToast
from django.utils.http import urlquote

from common import BaseProvider


# Testare questa lib https://pypi.python.org/pypi/python-mpns/0.1.3
# Eventualmente provare approccio low level http://stackoverflow.com/questions/19366308/python-windows-phone-8-authenticated-push


class WP8PushProvider(BaseProvider):

    def pushMessage(self, message, destToken, channel_name):
        send_count = len(destToken)
        sent = 0
        if send_count > 0:

            toast = MPNSToast()

            # Nota il body per sicurezza va mandato solo in versione "short" per il tile
            # ma i dati del messaggio li prende l'app con una get sull'id
            paramString = "?body=" + urlquote(message.alert_msg) + "&push_type=" + message.push_type + "&"

            for k in message.data_dic:
                paramString += k + "=" + str(urlquote(message.data_dic[k])) + "&"

            for tok in destToken:
                toast.send(tok, {'text1': message.alert_msg, 'text2': 'Pushetta', 'param': paramString[:-1]})
                sent = sent + 1
        else:
             self.log_info("Nothing to send for WP8PushProvider")


        return sent
