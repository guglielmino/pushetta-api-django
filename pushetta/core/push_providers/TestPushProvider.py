# coding=utf-8

# Progetto: Pushetta API
# Fake push provider for test only

from common import PushMessage, BaseProvider, PushProviderException


class TestPushProvider(BaseProvider):
    def pushMessage(self, message, tokens, channel_name):
        if not isinstance(tokens, list):
            raise PushProviderException("tokens must be a list")
            return False

        if not isinstance(message, PushMessage):
            raise PushProviderException("message must be a PushMessage")
            return False

        return True