# coding=utf-8

# Progetto: Pushetta API
# Layer con logica di business condivisa

import logging

logger = logging.getLogger(__name__)


from django.conf import settings

from django.template.loader import get_template
from django.template import Context
from django.core.urlresolvers import reverse

from core.models import Channel, ChannelMsg, ChannelSubscribeRequest
from core.models import ChannelSubscribeRequest, Subscriber

from core.models import PUBLIC, PRIVATE
from core.models import PENDING, ACCEPTED, REJECTED

from core.push_manager import PushProviderFactory, providers_map
from core.push_providers.common import PushMessage
from core.subscriber_manager import SubscriberManager

from haystack.query import SearchQuerySet
from haystack.inputs import Clean

from core.security_helpers import OTTManager

from core.tasks import push_messages, read_feedback_multi, sendMailMessage, get_screenshot
from core.utility import check_for_url


def get_suggested_channels():
    # I canali suggeriti al momento sono quelli con maggior numero di subscriptions
    return Channel.objects.filter(hidden=False).order_by('-subscriptions')[:10]


def send_push_message(channel, mime_type, body, expire, target=None):
    """
    Creazione del messaggio persistente
    :param channel: channel object
    :param mime_type: type of message (only plain/text at this time)
    :param body: message doby
    :param expire: date of expiration of notification (max 1 month)
    :param target: optional target to select which kind of devices must receive push
    :return:
    """
    msg = ChannelMsg(channel=channel)
    # msg.channel = channel
    msg.message_type = mime_type
    msg.body = body
    msg.expire = expire
    msg.save()

    # Gestione del token di autenticazione allegato al push message
    ott = OTTManager(settings.OTT_DURATION_SECONDS).getOneTimeToken()

    # Creazione del messaggio da "pushare"
    extra_data = {"message_id": msg.id, "channel_name": channel.name, "channel_image_url": channel.image,
                  "ott": ott}
    pmsg = PushMessage(alert_msg=msg.body[:100],
                       push_type="plain_push",
                       data_dic=extra_data)


    # Di default tutti i target, se specificato solo quelli filtrati
    targets = get_push_targets()
    if not target is None:
        targets = filter(lambda t: t == target, targets)
        
    target_string = " ".join(targets)
    logger.info("send_push_message::Pushing to platform {0}".format(target_string))

    # Nota i token vengono estratti per piattaforma
    for platform in targets:
        if settings.ENVIRONMENT == "dev":
            push_messages.apply(args=[pmsg, channel.name, platform]).get()
        else:
            push_messages.delay(pmsg, channel.name, platform)

    # Gestione del grab dell'eventuale url presente nel testo del messaggio
    urls = check_for_url(msg.body)
    if not urls is None and len(urls) > 0:
        url = urls[-1]
        if settings.ENVIRONMENT == "dev":
            get_screenshot.apply(args=[url, msg.id])
        else:
            get_screenshot.delay(url, msg.id)

    return SendPushResponse(success=True, error_code="")

def get_push_targets():
    return providers_map.keys()

def search_public_channels(query):
    """
    Search of channels
    :param query: query for search
    :return: SearchResult
    """
    sqs = SearchQuerySet().models(Channel).filter_or(name__contains=Clean(query)).filter_or(
        description__contains=Clean(query))
    return sqs.filter(hidden='false') # Note: with False (Python Standard bool value) the Elasticsearch query is wrong


def set_read_feedback_multiple(deviceId, messageIds):
    """
    Set read status for one or more messages
    :param deviceId: sender device
    :param messageIds: array of messages ids
    :return:
    """
    read_feedback_multi.delay(deviceId, messageIds)


class SendPushResponse(object):
    def __init__(self, success, error_code):
        """

        :type success: bool
        """
        self.success = success
        self.error_code = error_code


class SubscribeResponse(object):
    SUBSCRIBED = 0
    REQUEST_SEND = 1
    ERROR = 2


def ask_subscribe_channel(channel, device_id):
    """
    Ask for subscribe to a channel. If public subscription is immediate else a request
    to channel owner is generated
    :param channel:
    :param device_id:
    """

    try:
        asking_subscriber = Subscriber.objects.get(device_id=device_id)

        # Verifico che non sia già sottoscritto il canale (nel caso rispondo semplicemente con 200 OK)
        subscription = SubscriberManager().get_subscription(channel.name, asking_subscriber.sub_type, device_id)
        if subscription is None:
            if channel.kind == PUBLIC:
                SubscriberManager().subscribe(channel.name, asking_subscriber.sub_type, device_id,
                                              asking_subscriber.token)
                # Inc num subscriptions
                channel.subscriptions = channel.subscriptions + 1
                channel.save()
                return SubscribeResponse.SUBSCRIBED
            elif channel.kind == PRIVATE:
                # Viene creata la richiesta di subscription
                # e al cliamante la risposta sarà NOT_AUTHORIZED

                if not ChannelSubscribeRequest.objects.filter(device_id=device_id).filter(channel=channel).exists():
                    subscribe_request = ChannelSubscribeRequest(device_id=device_id, channel=channel, status=PENDING)
                    subscribe_request.save()


                # Segnalazione via mail all'owner del canale
                send_authrequest_email(channel, asking_subscriber)

                return SubscribeResponse.REQUEST_SEND

    except Subscriber.DoesNotExist:
        return SubscribeResponse.ERROR


def subscribe_to_channel(subscriber, channel):
    subscription = SubscriberManager().get_subscription(channel.name, subscriber.sub_type, subscriber.device_id)
    if subscription is None:
        SubscriberManager().subscribe(channel.name, subscriber.sub_type, subscriber.device_id, subscriber.token)
        # Inc num subscriptions
        channel.subscriptions = channel.subscriptions + 1
        channel.save()


def change_request_status(request, new_status):
    if new_status == ACCEPTED:
        subscriber = Subscriber.objects.get(device_id=request.device_id)
        subscribe_to_channel(subscriber, request.channel)
        # La richiesta accettata genera una sottoscrizione e sparisce
        request.delete()
    elif new_status == REJECTED:
        # update della richiesta (VANNO POI FILTRATE IN USCITA)
        request.status = new_status
        request.save()


def send_authrequest_email(channel, request):
    body = get_template('email/email_subscribe_request.txt')

    ctx = Context({
        'dev_name': request.name,
        'channel_name': channel.name,
        'channel_admin_url': reverse('my-channelview', args=[channel.name])
    })
    sendMailMessage.delay(u"Subscribe request for channel {0}".format(channel.name), body.render(ctx),
                          [channel.owner.email])


def unsubscribe_channel(channel, device_id):
    """
    Unsubscribe a device from a channel
    :param channel:
    :param device_id:
    """
    subscriber = Subscriber.objects.get(device_id=device_id)
    result = False
    if not channel is None and not device_id is None:
        result = True
        subManager = SubscriberManager()

        sub_token = subManager.get_subscription(channel.name, subscriber.sub_type, subscriber.device_id)
        if not sub_token is None:

            subManager.unsubscribe(channel.name, subscriber.device_id, subscriber.sub_type)

            # Dec num subscriptions
            channel.subscriptions = channel.subscriptions - 1
            channel.save()
        else:
            # Verifica che non si tratti di una subscription nel caso la cancella
            reqs = ChannelSubscribeRequest.objects.filter(device_id=subscriber.device_id).filter(channel=channel)
            if reqs.count() > 0:
                reqs[0].delete()
            else:
                result = False
    return result


def get_device_subscriptions(device_id):
    """
    get all channel subscribed by a device
    :param device_id:
    """

    channel_names = SubscriberManager().get_device_subscriptions(device_id)

    # Uso ChannelSubscribeRequestSerializer e quelli già sottoscritti li aggiungo fake come ACCEPTED
    channels = Channel.objects.filter(name__in=channel_names)
    subscribed = [ChannelSubscribeRequest(channel=ch, device_id=device_id, status=ACCEPTED) for ch in channels]
    # Le richieste visualizzate client side sono solo quelle
    requests = ChannelSubscribeRequest.objects.filter(device_id=device_id).filter(status=PENDING)
    return subscribed + list(requests)

