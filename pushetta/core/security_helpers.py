# coding=utf-8

import hmac
import hashlib
import base64
import string
import random

import redis
from django.conf import settings


class OTTManager():
    """
    Handler of One Time Token
    """

    key_pattern = "{0}:ott:{1}"

    def __init__(self, ott_expire_seconds):
        pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        self.redis_client = redis.Redis(connection_pool=pool)
        self.ott_expire_seconds = ott_expire_seconds

    def getOneTimeToken(self):
        ott = self.__random_string_generator()
        # Il contenuto della chiave è insignificante, il token è rapresentato dall'esistenza della chiave stessa
        key = self.__get_key(ott)
        self.redis_client.set(key, 1)
        self.redis_client.expire(key, self.ott_expire_seconds)
        return ott


    def consumeOneTimeToken(self, ott):
        ret = False
        key = self.__get_key(ott)
        if self.redis_client.exists(key):
            self.redis_client.delete(key)
            ret = True

        return ret

    def existsOneTimeToken(self, ott):
        key = self.__get_key(ott)
        return self.redis_client.exists(key)

    def __random_string_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(string.ascii_uppercase) for i in range(size))
        # return ''.join(random.choice(chars) for _ in range(size))

    def __get_key(self, ott):
        return self.key_pattern.format(settings.REDIS_KEY_PREFIX, ott)


# Nota: seed è meglio che sia 20 caratteri
def computeSignature(self, seed, contentType, dateString, methodPath):
    """
    Compute the signature to validate devices requeste
    seed -- seed shared with devices with push notifications
    contentType -- value of http header Content-Type
    dateString -- UTC string with request date dd-mm-yyyy format
    methodPath -- method of API request (absolute path)
    """
    # Nota: il seed è il seme condiviso tra client e server, se compromesso va cambiato
    # viene condiviso mediante notifiche push
    key = "4kGSVVETG8Ox/sF6zy6dFCpO97A3wUHr9jc41441"
    data = "POST\n\n{0}\n{1}\n{2}".format(contentType, dateString, methodPath)

    cKey = key.encode('ascii', 'ignore')
    cData = data.encode('ascii', 'ignore')

    dig = hmac.new(cKey, msg=cData, digestmod=hashlib.sha256).digest()
    b64HmacSha256 = base64.b64encode(dig).decode()  # py3k-mode
    ret = "{1}:{0}".format(seed, b64HmacSha256)
    return ret
