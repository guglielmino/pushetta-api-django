# Progetto: Pushetta API 
# Test for core app 

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from datetime import datetime
from dateutil.relativedelta import relativedelta

from core.models import *
from core.push_providers.common import PushProviderException
from core.services import *
from core.tasks import *

from core.utility import *


class ModelsTestCase(TestCase):
    def test_Channel(self):
        ch = Channel()

        ch.name = "Test channel"
        ch.image = 'http://www.iconpng.com/png/pictograms/bell.png'
        ch.description = "bla bla"
        ch.kind = PUBLIC
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()
        self.assertTrue(ch.id > 0, "Channel model NOT saved")

    def test_ChannelMsg(self):
        ch = Channel()

        ch.name = "Test channel"
        ch.image = 'http://www.iconpng.com/png/pictograms/bell.png'
        ch.description = "bla bla"
        ch.kind = PUBLIC
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()

        msg = ChannelMsg(channel=ch)
        msg.message_type = 'text/plain'
        msg.body = 'bla bla bla'
        msg.expire = datetime.utcnow() + relativedelta(days=1)

        msg.save()

        self.assertTrue(msg.id > 0, "ChannelMsg model NOT saved")

    def test_ChannelMsg_with_urlpreview(self):
        ch = Channel()

        ch.name = "Test channel"
        ch.image = 'http://www.iconpng.com/png/pictograms/bell.png'
        ch.description = "bla bla"
        ch.kind = PUBLIC
        ch.hidden = False
        ch.subscriptions = 0
        ch.save()

        msg = ChannelMsg(channel=ch)
        msg.message_type = 'text/plain'
        msg.body = 'bla bla bla'
        msg.expire = datetime.utcnow() + relativedelta(days=1)
        msg.preview_url = "http://www.pushetta.com/uploads/url_previews/a1fd950f726fa1b971c94d527eca1287606ef4fe437cfca2be6eecab518460a8.thumb.png"


        msg.save()

        self.assertTrue(msg.id > 0, "ChannelMsg model NOT saved")
        self.assertIsNotNone(msg.preview_url, "preview_url is None")

    def test_Subscriber(self):
        sub = Subscriber()
        sub.sub_type = 'text/plain'
        sub.device_id = '2222222222'
        sub.token = 'tokko'
        sub.enabled = True
        sub.name = 'my name'
        sub.sandbox = False

        sub.save()

        self.assertTrue(sub.device_id > 0, "Subscriber model NOT saved")

    def test_ChannelMsgDefaultExpire(self):
        ch = Channel()

        ch.name = "Test channel exp"
        ch.image = 'http://www.iconpng.com/png/pictograms/bell.png'
        ch.description = "bla bla"
        ch.kind = PUBLIC
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()

        msg = ChannelMsg(channel=ch)
        msg.message_type = 'text/plain'
        msg.body = 'bla bla bla'

        msg.save()

        attended_expire = datetime.today() + relativedelta(months=1)

        self.assertTrue(msg.expire.date() == attended_expire.date(), "ChannelMsg expire WRONG")


class SubscribeManagerTestCase(TestCase):
    """
    Test cases for SubscribeManager
    """

    def setUp(self):
        settings.REDIS_DB = 15  # Db usato per i test
        self.manager = SubscriberManager()
        self.manager.flushdb()

    def test_subscribe(self):
        self.manager.subscribe('test_channel', 'type', 'devid', 'token')
        res = self.manager.get_subscription('test_channel', 'type', 'devid')
        self.assertEqual(res, 'token')

    def test_unsubscribe(self):
        self.manager.subscribe('test_channel_un', 'type_un', 'devid_un', 'token')
        self.manager.unsubscribe('test_channel_un', 'devid_un', 'type_un')
        res = self.manager.get_subscription('test_channel_un', 'type_un', 'devid_un')
        self.assertEqual(res, None)

    def test_get_subscribers(self):
        self.manager.subscribe('test_channel1', 'type1', 'devid1', 'token1')
        self.manager.subscribe('test_channel1', 'type1', 'devid2', 'token2')
        self.manager.subscribe('test_channel1', 'type1', 'devid3', 'token3')

        subs = self.manager.get_subscribers('test_channel1', 'type1')
        self.assertEqual(len(subs), 3)
        self.assertTrue('token3' in subs)

    def test_get_device_subscriptions(self):
        self.manager.subscribe('test_channel1', 'type1', 'device1', 'token1')
        self.manager.subscribe('test_channel2', 'type1', 'device1', 'token1')
        self.manager.subscribe('test_channel3', 'type1', 'device1', 'token1')

        subscriptions = self.manager.get_device_subscriptions('device1')
        self.assertEqual(len(subscriptions), 3)

    def test_device_unsubscribe(self):
        self.manager.subscribe('test_channel1', 'type1', 'device1', 'token1')
        self.manager.subscribe('test_channel2', 'type1', 'device1', 'token1')
        self.manager.subscribe('test_channel3', 'type1', 'device1', 'token1')

        self.manager.unsubscribe('test_channel1', 'device1', 'type1')

        subscriptions = self.manager.get_device_subscriptions('device1')
        self.assertEqual(len(subscriptions), 2)

    def test_get_all_subscribers(self):
        self.manager.subscribe('test_channel1', 'type1', 'devid1', 'token1')
        self.manager.subscribe('test_channel1', 'type2', 'devid2', 'token2')
        self.manager.subscribe('test_channel1', 'type3', 'devid3', 'token3')

        subs = self.manager.get_all_subscribers('test_channel1')
        self.assertEqual(len(subs), 3)
        self.assertTrue('token1' in subs)
        self.assertTrue('token2' in subs)
        self.assertTrue('token3' in subs)

    def test_channel_subscription_ignore_case(self):
        self.manager.subscribe('AChannelWithCase', 'type1', 'device1', 'token1')

        subscriptions = self.manager.get_subscribers('achannelwithcase', 'type1')
        self.assertEqual(len(subscriptions), 1)
        self.assertEqual(subscriptions[0], 'token1')


    def test_del_channel_remove_subscriptions(self):
        channel_name = "ChannelDelTest"

        ch = Channel()

        ch.name = channel_name
        ch.image = 'http://www.iconpng.com/png/pictograms/bell.png'
        ch.description = "bla bla"
        ch.kind = PUBLIC
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()

        sub1 = Subscriber()
        sub1.sub_type = 'type1'
        sub1.token = 'token1'
        sub1.device_id = 'devid1'
        sub1.save()

        sub2 = Subscriber()
        sub2.sub_type = 'type2'
        sub2.token = 'token2'
        sub2.device_id = 'devid2'
        sub2.save()

        self.manager.subscribe(channel_name, sub1.sub_type, sub1.device_id, sub1.token)
        self.manager.subscribe(channel_name, sub2.sub_type, sub2.device_id, sub2.token)

        subscriptions = self.manager.get_all_subscribers(channel_name)
        self.assertEqual(len(subscriptions), 2)

        ch.delete()

        subs_post_del = self.manager.get_all_subscribers(channel_name)
        # IN AMBIENTE DI TEST IL SIGNAL DI DELETE NON VIENE TRIGGERATO ED IL TEST FALLISCE...
        self.assertEqual(len(subs_post_del), 0)


class PushProvidersTestCase(TestCase):
    """
    Test cases for Push Providers
    """

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        settings.ENVIRONMENT = "dev"

    def test_fake_pushprovider_success(self):
        provider = PushProviderFactory.create('test', None)

        msg = PushMessage('alert text', 'plain_push', {'key': 'value'})

        res = provider.pushMessage(msg, ['token'], "a channel")
        self.assertEqual(res, True)

    def test_fake_pushprovider_argumentsfail(self):
        provider = PushProviderFactory.create('test', None)
        self.assertRaises(PushProviderException, provider.pushMessage, 'wrong message', ['token'], "a channel")


class OTTTestCase(TestCase):
    """
    Test cases for OneTimeToken
    """

    def setUp(self):
        settings.REDIS_DB = 15  # Db usato per i test
        self.manager = SubscriberManager()
        self.manager.flushdb()

    def test_ott_create(self):
        ottmanager = OTTManager(100)
        ott = ottmanager.getOneTimeToken()
        self.assertTrue(len(ott) > 0, "OTT is not valid")


    def test_ott_unique(self):
        ottmanager = OTTManager(100)
        ott = ottmanager.getOneTimeToken()
        self.assertTrue(len(ott) > 0, "OTT is not valid")
        ott2 = ottmanager.getOneTimeToken()
        self.assertFalse(ott == ott2, "OTT is not unique")

    def test_ott_consume(self):
        ottmanager = OTTManager(100)
        ott = ottmanager.getOneTimeToken()
        self.assertTrue(len(ott) > 0, "OTT is not valid")
        res = ottmanager.consumeOneTimeToken(ott)
        self.assertTrue(res, "OTT consume failed")
        res = ottmanager.existsOneTimeToken(ott)
        self.assertFalse(res, "OTT exist after consume")


class BusinessServicesTestCase(TestCase):
    def setUp(self):
        settings.REDIS_DB = 15  # Db usato per i test
        self.manager = SubscriberManager()
        self.manager.flushdb()


    def test_set_read_feedback(self):
        ch = Channel()

        ch.name = "Test read feedback"
        ch.image = 'http://www.iconpng.com/png/pictograms/bell.png'
        ch.description = "A channel description"
        ch.kind = PUBLIC
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()

        msg = ChannelMsg(channel=ch)
        msg.message_type = 'text/plain'
        msg.body = 'some text 1'

        msg.save()

        msg2 = ChannelMsg(channel=ch)
        msg2.message_type = 'text/plain'
        msg2.body = 'some text 2'

        msg2.save()

        # TODO: Verificare come testare il task celery, il codice seguente ne replica il comportamento
        # read_feedback_multi.apply("1234", [msg.id, msg2.id])

        for msgId in [msg.id, msg2.id]:
            msg = ChannelMsg.objects.get(id=msgId)
            c = msg.channel.name

            FeedbackManager().setFeedback(c, msgId, "1234")

        count = FeedbackManager().getFeedbackCount(ch.name, msg.id)
        print "count {0}".format(count)
        self.assertTrue(count == 1)


    def test_private_channel_subscribe(self):
        u = User()
        u.username = "sample"
        u.first_name = "Sample"
        u.email = "sample@nowhere.org"
        u.set_password("123")
        u.save()

        ch = Channel()

        ch.owner = u
        ch.name = "Test private"
        ch.image = 'http://www.iconpng.com/png/pictograms/bell.png'
        ch.description = "A channel description"
        ch.kind = PRIVATE
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()

        sub1 = Subscriber()
        sub1.sub_type = 'type1'
        sub1.token = 'token1'
        sub1.device_id = 'devid1'
        sub1.save()

        resp = ask_subscribe_channel(ch, 'devid1')

        self.assertEqual(resp, SubscribeResponse.REQUEST_SEND)


    def test_private_channel_multiple_subscribe(self):
        u = User()
        u.username = "sample_m"
        u.first_name = "Sample"
        u.email = "sample_m@nowhere.org"
        u.set_password("123")
        u.save()

        ch = Channel()

        ch.owner = u
        ch.name = "Test private2"
        ch.image = 'http://www.iconpng.com/png/pictograms/bell.png'
        ch.description = "A channel description"
        ch.kind = PRIVATE
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()

        sub1 = Subscriber()
        sub1.sub_type = 'type2'
        sub1.token = 'token2'
        sub1.device_id = 'devid_m'
        sub1.save()

        # First request
        resp = ask_subscribe_channel(ch, 'devid_m')

        self.assertEqual(resp, SubscribeResponse.REQUEST_SEND)

        # Second request
        resp = ask_subscribe_channel(ch, 'devid_m')

        self.assertEqual(resp, SubscribeResponse.REQUEST_SEND)

        # Must be present only 1 request
        req_count = ChannelSubscribeRequest.objects.filter(device_id='devid_m').filter(channel=ch).count()
        self.assertEqual(req_count, 1)


    def test_public_channel_subscribe(self):
        u = User()
        u.username = "samplep"
        u.first_name = "Samplep"
        u.email = "samplep@nowhere.org"
        u.set_password("123")
        u.save()

        ch = Channel()

        ch.owner = u
        ch.name = "Test public"
        ch.image = 'http://www.google.com'
        ch.description = "A channel description"
        ch.kind = PUBLIC
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()

        sub1 = Subscriber()
        sub1.sub_type = 'type2'
        sub1.token = 'token2'
        sub1.device_id = 'devid2'
        sub1.save()

        resp = ask_subscribe_channel(ch, 'devid2')

        self.assertEqual(resp, SubscribeResponse.SUBSCRIBED)

    def test_no_subscriber_channel_subscribe(self):
        u = User()
        u.username = "samplen"
        u.first_name = "Samplen"
        u.email = "samplen@nowhere.org"
        u.set_password("123")
        u.save()

        ch = Channel()

        ch.owner = u
        ch.name = "Test no subs"
        ch.image = 'http://www.google.com'
        ch.description = "A channel description"
        ch.kind = PUBLIC
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()

        resp = ask_subscribe_channel(ch, 'devid3')

        self.assertEqual(resp, SubscribeResponse.ERROR)

    def test_request_statuses(self):
        u = User()
        u.username = "sample_pen1"
        u.first_name = "Sample"
        u.email = "sample_pen1@nowhere.org"
        u.set_password("123")
        u.save()

        ch = Channel()

        ch.owner = u
        ch.name = "Test private pen"
        ch.image = 'http://www.iconpng.com/png/pictograms/bell.png'
        ch.description = "A channel description"
        ch.kind = PRIVATE
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()

        sub1 = Subscriber()
        sub1.sub_type = 'type2'
        sub1.token = 'token2'
        sub1.device_id = 'devid_pen1'
        sub1.save()

        # First request
        resp = ask_subscribe_channel(ch, 'devid_pen1')

        self.assertEqual(resp, SubscribeResponse.REQUEST_SEND)

        # Must be present only 1 request
        requests = ChannelSubscribeRequest.objects.filter(device_id='devid_pen1').filter(channel=ch)
        self.assertEqual(requests.count(), 1)
        self.assertEqual(requests[0].status, PENDING)

        change_request_status(requests[0], REJECTED)
        self.assertEqual(requests[0].status, REJECTED)

        change_request_status(requests[0], ACCEPTED)
        res = self.manager.get_subscription("Test private pen", 'type2', 'devid_pen1')

        self.assertEqual(res, 'token2')

        requests = ChannelSubscribeRequest.objects.filter(device_id='devid_pen1').filter(channel=ch)
        self.assertEqual(requests.count(), 0)


    def test_unsubscribe(self):
        u = User()
        u.username = "sample_un"
        u.first_name = "Sample_un"
        u.email = "sample_un@nowhere.org"
        u.set_password("123")
        u.save()

        ch = Channel()

        ch.owner = u
        ch.name = "Test unsub"
        ch.image = 'http://www.google.com'
        ch.description = "A channel description"
        ch.kind = PUBLIC
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()

        sub1 = Subscriber()
        sub1.sub_type = 'type2'
        sub1.token = 'token2'
        sub1.device_id = 'devid3'
        sub1.save()

        resp = ask_subscribe_channel(ch, 'devid3')

        self.assertEqual(resp, SubscribeResponse.SUBSCRIBED)

        res = unsubscribe_channel(ch, 'devid3')

        self.assertEqual(res, True)

    def test_subscriptions_list(self):
        u = User()
        u.username = "sample_un"
        u.first_name = "Sample_un"
        u.email = "sample_un@nowhere.org"
        u.set_password("123")
        u.save()

        ch1 = Channel()

        ch1.owner = u
        ch1.name = "Test lst1"
        ch1.image = 'http://www.google.com'
        ch1.description = "A channel description"
        ch1.kind = PUBLIC
        ch1.hidden = False
        ch1.subscriptions = 0

        ch1.save()

        ch2 = Channel()

        ch2.owner = u
        ch2.name = "Test lst2"
        ch2.image = 'http://www.google.com'
        ch2.description = "A channel description"
        ch2.kind = PUBLIC
        ch2.hidden = False
        ch2.subscriptions = 0

        ch2.save()

        sub1 = Subscriber()
        sub1.sub_type = 'type2'
        sub1.token = 'token2'
        sub1.device_id = 'devid4'
        sub1.save()

        resp = ask_subscribe_channel(ch1, 'devid4')
        self.assertEqual(resp, SubscribeResponse.SUBSCRIBED)

        resp = ask_subscribe_channel(ch2, 'devid4')
        self.assertEqual(resp, SubscribeResponse.SUBSCRIBED)

        res = get_device_subscriptions('devid4')

        self.assertEqual(len(res), 2)

        print [c.channel.name for c in res]


    def test_push_message_with_url(self):
        ch = Channel()

        ch.name = "Url test"
        ch.image = 'http://www.google.com'
        ch.description = "A channel description"
        ch.kind = PUBLIC
        ch.hidden = False
        ch.subscriptions = 0

        ch.save()

        send_push_message(ch, "plain/text", "a test with http://www.facebook.com url", datetime.now())


class UtilityTestCase(TestCase):

    def setUp(self):
        settings.REDIS_DB = 15  # Db usato per i test


    def test_find_single_url(self):
        sample = "a sample text with www.pushetta.com a single url"
        res = check_for_url(sample)
        self.assertTrue(len(res) == 1)
        self.assertTrue(res[0] == "www.pushetta.com")


    def test_find_many_url(self):
        sample = "a sample text with www.pushetta.com and www.libero.it two urls"
        res = check_for_url(sample)
        self.assertTrue(len(res) == 2)
        self.assertTrue(res[0] == "www.pushetta.com")
        self.assertTrue(res[1] == "www.libero.it")


    def test_find_no_url(self):
        sample = "a sample text without urls"
        res = check_for_url(sample)
        self.assertTrue(len(res) == 0)

    def test_complex_url(self):
        sample = "a sample test with a http://upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Logo_Google_2013_Official.svg/2000px-Logo_Google_2013_Official.svg.png complex url"
        res = check_for_url(sample)
        self.assertTrue(len(res) == 1)
        self.assertEqual(res[0], "upload.wikimedia.org/wikipedia/commons/thumb/a/aa/Logo_Google_2013_Official.svg/2000px-Logo_Google_2013_Official.svg.png")


    def test_grab_url_screenshot(self):
        url = "http://www.kapipal.com/"
        res = grab_url_screenshot(url)

        self.assertTrue(res)


class TasksTestCases(TestCase):
    def setUp(self):
        # NOTA: Importante per attivare il sistema di test di Celery
        settings.TEST_RUNNER = 'djcelery.contrib.test_runner.CeleryTestSuiteRunner'

        settings.REDIS_DB = 15  # Db usato per i test
        self.manager = SubscriberManager()
        self.manager.flushdb()

    def test_url_screenshot(self):
        ch = Channel()

        ch.name = "Test grab"
        ch.image = ''
        ch.description = "bla bla"
        ch.kind = PUBLIC
        ch.hidden = False
        ch.subscriptions = 0
        ch.save()

        msg = ChannelMsg(channel=ch)
        msg.message_type = 'text/plain'
        msg.body = 'bla bla bla'
        msg.expire = datetime.utcnow() + relativedelta(days=1)

        msg.save()

        res = get_screenshot.delay('https://www.google.com', msg.id)
        self.assertIsNotNone(res, "Screenshot failed")

        msg = ChannelMsg.objects.get(id=7)
        self.assertIsNotNone(msg.preview_url)




