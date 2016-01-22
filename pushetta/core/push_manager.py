# coding=utf-8

# Progetto: Pushetta API 
# Classes for interact with push server (Google Cloud Messaging, Apple Push Notification Server, ...)

from push_providers.iOSPushProvider import iOSPushProvider
from push_providers.AndroidPushProvider import AndroidPushProvider
from push_providers.WP8PushProvider import WP8PushProvider
from push_providers.TestPushProvider import TestPushProvider
from push_providers.SafariPushProvider import SafariPushProvider
from push_providers.MQTTPushProvider import MQTTPushProvider

"""
Known push providers
"""
providers_map = {
    'ios': iOSPushProvider(),
    'android': AndroidPushProvider(),
    'wp8': WP8PushProvider(),
    'test': TestPushProvider(),
    'safari': SafariPushProvider(),
    'chrome': AndroidPushProvider(),
    'iot_device': MQTTPushProvider(),
}


class PushProviderFactory:
    """
    Factory class for different push providers
    """

    @staticmethod
    def create(providerType, logger):
        if not providerType in providers_map:
            assert 1, "Bad provider creation: " + providerType
            return None
        else:
            pusher = providers_map[providerType]
            pusher.logger = logger
            return pusher






      
