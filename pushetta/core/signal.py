# coding=utf-8

# Progetto: Pushetta Core
# Handling dei signals sui modelli

import logging
from datetime import datetime
from dateutil.relativedelta import relativedelta

logger = logging.getLogger(__name__)

from django.dispatch import receiver
from django.db.models.signals import pre_delete, pre_save

from core.services import unsubscribe_channel
from core.models import Channel, Subscriber, ChannelMsg

from core.subscriber_manager import SubscriberManager

'''
Signal post delete del Channel che cancella i subscriber 
'''


@receiver(signal=pre_delete, sender=Channel)
def pre_remove_channel(sender, **kwargs):
    channel = kwargs.get('instance')
    sub_manager = SubscriberManager()
    sub_tokens = sub_manager.get_all_subscribers(channel.name)
    devices = Subscriber.objects.filter(token__in=sub_tokens)

    logger.info("Delete channel ({0}) signal ".format(channel.name))

    for dev in devices.all():
        logger.info("\t removing subscriber {0}".format(dev.device_id))
        unsubscribe_channel(channel, dev.device_id)


'''
Signal post delete del Subscriber che cancella le sue sottoscrizioni
'''


@receiver(signal=pre_delete, sender=Subscriber)
def pre_remove_subscription(sender, **kwargs):
    subscriber = kwargs.get('instance')
    sub_manager = SubscriberManager()
    subscriptions = sub_manager.get_device_subscriptions(subscriber.device_id)

    logger.info("Delete subscriber ({0} - {1}) signal ".format(subscriber.name, subscriber.sub_type))

    for channel_name in subscriptions:
        unsubscribe_channel(channel, subscriber.device_id)


'''
Signal pre save del messaggio per bonificare l'expire se non passato
'''


@receiver(signal=pre_save, sender=ChannelMsg)
def pre_default_expire(sender, **kwargs):
    channelMsg = kwargs.get('instance')
    if not channelMsg.expire:
        channelMsg.expire = (datetime.utcnow() + relativedelta(months=1))