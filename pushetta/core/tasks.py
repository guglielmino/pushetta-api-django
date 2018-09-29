# coding=utf-8

# Progetto: Pushetta API 
# Task asincroni gestiti da celery


from celery.task.schedules import crontab
from celery.task import task, periodic_task
from celery.utils.log import get_task_logger

from core.models import ChannelMsg

from core.push_manager import PushProviderFactory
from core.subscriber_manager import SubscriberManager
from core.feedback_manager import FeedbackManager
from core.utility import grab_url_screenshot

# Per l'uso email standard Django
from django.core.mail import EmailMessage

from django.core.cache import cache

logger = get_task_logger(__name__)


@task(name='core.tasks.push_messages', ignore_result=False, max_retries=1)
def push_messages(pmsg, channel_name, platform):
    """

    :param pmsg: Message to push
    :param channel_name: Channel to push
    :param platform: Target platform
    """

    sub_tokens = SubscriberManager().get_subscribers(channel_name, platform)

    logger.debug("Pushing {0} tokens to channel {1} for platform {2}".format(len(sub_tokens), channel_name, platform))

    #  PUSH EFFETTIVO
    pusher = PushProviderFactory.create(platform, logger)
    pusher.pushMessage(pmsg, sub_tokens, channel_name)


@task(name='core.tasks.read_feedback_multi', ignore_result=True, max_retries=1)
def read_feedback_multi(deviceId, messageIds):
    """

    :param deviceId: Device id to mark read for
    :param messageIds: Array of id message to mark read
    """
    marked = 0
    try:
        for msgId in messageIds:

            msg = ChannelMsg.objects.get(id=msgId)
            c = msg.channel.name

            if FeedbackManager().setFeedback(c, msgId, deviceId) > 0:
                marked = marked + 1

    except ChannelMsg.DoesNotExist:
        logger.error("Trying to set read feedback on non existent message")

    return marked


@periodic_task(name='core.tasks.search_reindex', run_every=crontab(hour=4, minute=30))
def search_reindex():
    from haystack.management.commands import update_index

    update_index.Command().handle(using='default', remove=True)
    logger.info("Reindexing of search database")


@task(name='sendMailMessage', ignore_result=True, max_retries=1)
def sendMailMessage(subject, body, rcpts):
    msg = EmailMessage(subject, body, 'support@gumino.com', rcpts, headers={'Reply-To': 'no-reply@pushetta.com'})
    msg.send()

LOCK_EXPIRE = 60 * 5  # Lock expires in 5 minutes


@task(name='get_screenshot', max_retries=3)
def get_screenshot(url, message_id=None):
    # Questo task deve essere eseguito in modo seriale, solo uno in un dato
    # momento è attivo. Per questo si usa un lock
    ret = False
    lock_id = "screenshot_url-lock-id"
    acquire_lock = lambda: cache.add(lock_id, 'true', LOCK_EXPIRE)
    release_lock = lambda: cache.delete(lock_id)

    if acquire_lock():
        try:
            grabbed_url = grab_url_screenshot(url)
            if grabbed_url and message_id:
                message = ChannelMsg.objects.get(id=message_id)
                message.preview_url = grabbed_url
                message.save()

            ret = True
        except:
            logger.error("Try to run screenshot_url while already running")
        finally:
            release_lock()

        return ret






