# coding=utf-8

# Progetto: Pushetta API 
# Common for push providers


class PushMessage:
    """
    A single message to send, aler_msg is show by device when it receive the notification.
    data_dic is the payolad of message
    """

    def __init__(self, alert_msg, push_type, data_dic):
        self.alert_msg = alert_msg
        self.push_type = push_type
        self.data_dic = data_dic


class PushProviderException(Exception):
    pass


# Base class for all providers
class BaseProvider(object):
    logger = None
    
    def log_info(self, message):
        if self.logger != None:        
            self.logger.info(message) 
  
    def log_error(self, message):
        if self.logger != None:        
            self.logger.error(message) 
   
 
    def pushMessage(self, message, tokens, channel_name):
        raise NotImplementedError("Method must be implemented from subclass")
   