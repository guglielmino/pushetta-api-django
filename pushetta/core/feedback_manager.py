# coding=utf-8

# Progetto: Pushetta API 
# Manager for handling read feedback of channels messages

import redis
from django.conf import settings


class FeedbackManager():
    """
    This class mantain an Set for every message containing all devices
    who reads the message
    """


    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        self.redis_client = redis.Redis(connection_pool=pool)

    def setFeedback(self, channel_name, message_id, device_id):
        return self.redis_client.sadd(self.__getSetKey(channel_name, message_id), device_id)

    def getFeedbackCount(self, channel_name, message_id):
        return self.redis_client.scard(self.__getSetKey(channel_name, message_id))


    def __getSetKey(self, channel_name, message_id):
        return "{0}:{1}:{2}:{3}".format(settings.REDIS_KEY_PREFIX, "fback", channel_name, message_id)
