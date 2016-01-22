# coding=utf-8

# Progetto: Pushetta API 
# Wrapper for interaction with Subscriber storage (Redis)

# All strings in Unicode
from __future__ import unicode_literals

import redis
from django.conf import settings


class SubscriberManager():
    """
    This class mantain an Hash for every Channel containing all subscribers
    and a Set for every device containing all Channels subscribed
    """

    # Key part for hash key (subscriber to channel)
    subsc_key_part = "subsc"
    #  Key part for set with devices subscribing a channel
    subdev_key_part = "subdev"


    def __init__(self):
        pool = redis.ConnectionPool(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)
        self.redis_client = redis.Redis(connection_pool=pool)


    def flushdb(self):
        """
        WARNING: Remove all keys from current database
        """
        self.redis_client.flushdb()

    def subscribe(self, channel_name, sub_type, device_id, token):
        """
        Subscribe a device to a Channel
        """

        channel_name = channel_name.lower()

        key = self.__getHashKey(channel_name, sub_type)

        # Token in hash with Channel's subscribers
        self.redis_client.hset(key, self.__getFieldKey(device_id), token)
        skey = self.__getSetKey(device_id)
        # Channel name in set of channel subscribed by device
        self.redis_client.sadd(skey, channel_name)

    def unsubscribe(self, channel_name, device_id, sub_type):
        """
        Unsubscribe a device from a channel
        """

        channel_name = channel_name.lower()

        key = self.__getHashKey(channel_name, sub_type)
        # Token removed from hash with Channel's subscribers
        self.redis_client.hdel(key, self.__getFieldKey(device_id))
        # Channel name removed from set of channel subscribed by device
        skey = self.__getSetKey(device_id)
        self.redis_client.srem(skey, channel_name)


    def get_subscription(self, channel_name, sub_type, device_id):
        """
        Get channel subscription token for a device
        """

        channel_name = channel_name.lower()

        key = self.__getHashKey(channel_name, sub_type)
        field_value = self.redis_client.hget(key, self.__getFieldKey(device_id))
        return field_value


    def get_device_subscriptions(self, device_id):
        """
        Returns all Channel subscribed by a device
        """
        key = self.__getSetKey(device_id)
        return self.redis_client.smembers(key)

    def get_subscribers(self, channel_name, sub_type):
        """
        Return all tokens subscribing a channel
        """

        channel_name = channel_name.lower()

        key = self.__getHashKey(channel_name, sub_type)
        return self.redis_client.hvals(key)

    def get_all_subscribers(self, channel_name):
        """
        Return all tokens subscribing a channel
        """

        channel_name = channel_name.lower()

        keys = self.redis_client.keys(self.__getHashKeyPattern(channel_name))
        result = []
        for key in keys:
            for token in self.redis_client.hvals(key):
                result.append(token)
        return result


    def __getSetKey(self, device_id):
        return "{0}:{1}:{2}".format(settings.REDIS_KEY_PREFIX, self.subdev_key_part, device_id)

    def __getHashKeyPattern(self, channel_name):
        """
        Hash key composed by prefisx:subsc:channel_name:sub_type
        """
        return "{0}:{1}:{2}:*".format(settings.REDIS_KEY_PREFIX, self.subsc_key_part, channel_name)


    def __getHashKey(self, channel_name, sub_type):
        """
        Hash key composed by prefisx:subsc:channel_name:sub_type
        """
        return "{0}:{1}:{2}:{3}".format(settings.REDIS_KEY_PREFIX, self.subsc_key_part, channel_name, sub_type)

    def __getFieldKey(self, device_id):
        return device_id