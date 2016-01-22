# coding=utf-8

# Progetto: Pushetta API 
# Test for api app 


import json
import random
import string

from datetime import datetime, timedelta

from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.http import urlquote
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import AbstractUser, User

from core.models import *
from api.serializers import *
from core.subscriber_manager import SubscriberManager
from core.services import change_request_status


def rnd_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class SerializerTestCase(TestCase):
    """
    Test cases for serializers
    """

    def setUp(self):
        User.objects.create(first_name="fabrizio", last_name="gugliemino", email="guglielmino@gumino.com")
        ch = Channel.objects.create(name="Channel1", description="first channel", kind=PUBLIC)
        ChannelMsg.objects.create(body="a simple test", channel=ch, expire=datetime.today())

    def test_can_serialize_user(self):
        """User object serialization test"""
        user = User.objects.get(first_name="fabrizio")

        serializer = UserSerializer(user)
        self.assertEqual(serializer.data["first_name"] == "fabrizio", True)

    def test_can_serialize_channel(self):
        """Channel object serialization test"""
        channel = Channel.objects.get(name="Channel1")

        serializer = ChannelSerializer(channel)
        self.assertEqual(serializer.data["name"] == "Channel1", True)

    def test_can_serialize_channelmsg(self):
        """Channel object serialization test"""
        msg = ChannelMsg.objects.get(body="a simple test")

        serializer = ChannelMsgSerializer(msg)
        self.assertEqual(serializer.data["body"] == "a simple test", True)

class API_ChannelSubscriptionsTestCase(APITestCase):
    """
    Test cases for Channel API calls
    """

    def setUp(self):
        settings.REDIS_DB = 15  # Db usato per i test
        SubscriberManager().flushdb()

        sub1 = Subscriber()
        sub1.sub_type = 'type2'
        sub1.token = 'token2'
        sub1.device_id = 'devid_subs'
        sub1.save()

    def test_subscribe_channel_not_exist(self):
        """
        Test right response if try to register to inexistent Channel
        """
        channel_name = 'a channel'
        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = {'sub_type': 'ios', 'device_id': 'devid_subs', 'token': '2222'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_subscribe_channel_exist(self):
        """
        Test right response if try to register to existent Channel
        """
        channel_name = "Channel1"


        ch = Channel.objects.create(name=channel_name, description="mychannel", kind=PUBLIC)
        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = {'sub_type': 'ios', 'device_id': 'devid_subs', 'token': '2222'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_subscribe_channel_exist_counter(self):
        """
        Test right response if try to register to existent Channel and verify counter increment
        """
        channel_name = "Channel2"
        ch = Channel.objects.create(name=channel_name, description="mychannel", kind=PUBLIC)
        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = {'sub_type': 'ios', 'device_id': 'devid_subs', 'token': '2222'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        ch_updated = Channel.objects.get(id=ch.id)
        self.assertEqual(ch_updated.subscriptions, 1)


    def test_unsubscribe_channel_exist(self):
        """
        Test simple unsubscribe from channel
        """
        channel_name = "Channel_unsub"
        device_id = 'devid_subs'
        sub_type = 'android'
        token = '1234_unsub'


        sub_uns = Subscriber()
        sub_uns.sub_type = sub_type
        sub_uns.token = token
        sub_uns.device_id = device_id

        sub_uns.save()

        ch_owner = User()
        ch_owner.username = "username_unsub"
        ch_owner.first_name = "username_unsub"
        ch_owner.email = "ch_unsub@nowhere.org"
        ch_owner.set_password("123")
        ch_owner.save()

        ch = Channel.objects.create(owner=ch_owner, name=channel_name, description="", kind=PUBLIC)

        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = {'sub_type': sub_uns.sub_type, 'device_id': sub_uns.device_id, 'token': sub_uns.token}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('channels-api:unsubscribe-channel-by-name', args=[channel_name, sub_uns.sub_type, sub_uns.device_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unsubscribe_request(self):
        """
        Test unsubscribe (void in this case) from a channel subscribe request
        """
        channel_name = "Channel_unsub_req"
        device_id = 'devid_subs_req'
        token = 'token_req'
        sub_type = 'req_sub_type'

        sub1 = Subscriber()
        sub1.sub_type = sub_type
        sub1.token = token
        sub1.device_id = device_id
        sub1.save()

        ch_owner = User()
        ch_owner.username = "req_unsub"
        ch_owner.first_name = "req_unsub"
        ch_owner.email = "req_unsub@nowhere.org"
        ch_owner.set_password("123")
        ch_owner.save()

        ch = Channel.objects.create(owner=ch_owner, name=channel_name, description="", kind=PRIVATE)

        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = {'sub_type': sub_type, 'device_id': device_id, 'token': token}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        url = reverse('subscriptions-api:requests-list', args=[device_id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        url = reverse('channels-api:unsubscribe-channel-by-name', args=[channel_name, sub_type, device_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('subscriptions-api:requests-list', args=[device_id])
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)




    def test_unsubscribe_channel_exist_counter(self):
        """
        Test unsubscribe and subscription counter decrement
        """

        channel_name = "Channel_unsub_cnt"
        device_id = rnd_generator()
        sub_type = 'android'
        token = '567'

        sub_unsex = Subscriber()
        sub_unsex.sub_type = sub_type
        sub_unsex.token = token
        sub_unsex.device_id = device_id

        sub_unsex.save()

        ch_owner = User()
        ch_owner.username = "unsub_cnt"
        ch_owner.first_name = "unsub_cnt"
        ch_owner.email = "unsub_cnt@nowhere.org"
        ch_owner.set_password("123")
        ch_owner.save()


        ch = Channel.objects.create(owner=ch_owner, name=channel_name, description="", kind=PUBLIC)
        ch.subscriptions = 1
        ch.save()

        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = {'sub_type': sub_unsex.sub_type, 'device_id': sub_unsex.device_id, 'token': sub_unsex.token}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('channels-api:unsubscribe-channel-by-name', args=[channel_name, sub_unsex.sub_type, sub_unsex.device_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ch_updated = Channel.objects.get(id=ch.id)
        self.assertEqual(ch_updated.subscriptions, 1)

    def test_subscribe_private_channel(self):
        """
        Test subscribe to private channel and assert subscription counter remain invariate
        """

        ch_owner = User()
        ch_owner.username = "samplePrivate"
        ch_owner.first_name = "samplePrivate"
        ch_owner.email = "samplep@nowhere.org"
        ch_owner.set_password("123")
        ch_owner.save()

        channel_name = "Channel_priv1"
        ch = Channel.objects.create(owner=ch_owner, name=channel_name, description="private ch", kind=PRIVATE)
        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = {'sub_type': 'ios', 'device_id': 'devid_subs', 'token': '33333'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        ch_updated = Channel.objects.get(id=ch.id)
        self.assertEqual(ch_updated.subscriptions, 0)


class API_ChannelTestCase(APITestCase):
    """
    Test cases for Channel API calls
    """
    def test_suggested_channels(self):

        Channel.objects.create(name="First", description="", kind=PUBLIC, subscriptions=10)
        Channel.objects.create(name="Second", description="", kind=PUBLIC, subscriptions=8)
        Channel.objects.create(name="Third", description="", kind=PUBLIC, subscriptions=3)

        noDeviceId = None
        url = reverse('channels-api:channel-suggestions', args=[noDeviceId])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], "First")

    def test_suggested_channels_removing_subscriptions(self):
        sub1 = Subscriber()
        sub1.sub_type = 'android'
        sub1.token = 'aabbccdd'
        sub1.device_id = 'devid_sub'
        sub1.save()


        Channel.objects.create(name="First", description="", kind=PUBLIC, subscriptions=10)
        Channel.objects.create(name="Second", description="", kind=PUBLIC, subscriptions=8)
        Channel.objects.create(name="Third", description="", kind=PUBLIC, subscriptions=3)


        url = reverse('channels-api:subscribe-channel-by-name', args=["First"])
        data = {'sub_type': 'ios', 'device_id': 'devid_sub', 'token': '2222'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('channels-api:channel-suggestions', args=['devid_sub'])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

class API_PushTestCase(APITestCase):
    """
    Test cases for Pushes API calls
    """

    def __setAuthToken(self, username, password):
        url = reverse('auth-token')
        data = dict(username=username, password=password)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        auth_token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + auth_token)

    def setUp(self):
        settings.REDIS_DB = 15  # Db usato per i test
        settings.ENVIRONMENT = "dev"
        SubscriberManager().flushdb()

    def test_push_android(self):
        """
        Test right response trying to push on existent Channel for Android
        """
        self.user = User.objects.create_user("testuser", "testuser@nowhere.com", "123")
        self.user.save()


        sub1 = Subscriber()
        sub1.sub_type = 'android'
        sub1.token = 'APA91bHTYr7cTsCPtCATdsywKfw1eWeBhuhyPM7HSukVUEW6Ucxr5ueaeHjT2CrwLc1xvoQo-sbh_K6F_gMl4fJyagIVte5duLSEGbKhb9v-t6hKEAgdP6ROvYr7uG3Mh0on_aLE5S4NcjMI5JTdvPJrso-qO8m8bA'
        sub1.device_id = 'ffffffff-c97a-15d1-ffff-ffffef05ac4a'
        sub1.save()

        channel_name = 'AndroidChannelPush'
        ch = Channel.objects.create(name=channel_name, description="test for publish", kind=PUBLIC)
        ch.owner = self.user
        ch.save()

        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = dict(sub_type='android', device_id='ffffffff-c97a-15d1-ffff-ffffef05ac4a',
                    token='APA91bHTYr7cTsCPtCATdsywKfw1eWeBhuhyPM7HSukVUEW6Ucxr5ueaeHjT2CrwLc1xvoQo-sbh_K6F_gMl4fJyagIVte5duLSEGbKhb9v-t6hKEAgdP6ROvYr7uG3Mh0on_aLE5S4NcjMI5JTdvPJrso-qO8m8bA')

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.__setAuthToken(username="testuser", password="123")

        url = reverse('push-api:pushes-by-name', args=[channel_name])
        data = dict(body='a sample push', message_type='text/plain',
                    expire=datetime.today().strftime("%Y-%m-%d"))
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)

    def test_push_wp8(self):
        """
        Test right response trying to push on existent Channel for Windows Phone 8
        """
        self.user = User.objects.create_user("testuser", "testuser@nowhere.com", "123")
        self.user.save()

        sub1 = Subscriber()
        sub1.sub_type = 'wp8'
        sub1.token = 'http://db3.notify.live.net/throttledthirdparty/01.00/AQFQ8wh3rN7bRK74p2aYVzIFAgAAAAADAQAAAAQUZm52OkJCMjg1QTg1QkZDMkUxREQFBkVVTk8wMQ'
        sub1.device_id = '123456888'
        sub1.save()

        channel_name = 'Wp8ChannelPush'
        ch = Channel.objects.create(name=channel_name, description="test for publish", kind=PUBLIC)
        ch.owner = self.user
        ch.save()

        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = dict(sub_type='wp8', device_id='123456888',
                    token='http://db3.notify.live.net/throttledthirdparty/01.00/AQFQ8wh3rN7bRK74p2aYVzIFAgAAAAADAQAAAAQUZm52OkJCMjg1QTg1QkZDMkUxREQFBkVVTk8wMQ')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.__setAuthToken(username="testuser", password="123")
        url = reverse('push-api:pushes-by-name', args=[channel_name])
        data = dict(body='a sample push', message_type='text/plain', expire=datetime.today().strftime("%Y-%m-%d"))
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)

    def test_push_without_expire(self):
        """
        Test push something without passing expire
        """
        user = User.objects.create_user("usr_exp", "usr_exp@nowhere.com", "123")
        user.save()

        sub1 = Subscriber()
        sub1.sub_type = 'test'
        sub1.token = 'APA91bHTYr7cTsCPtCATdsywKfw1eWeBhuhyPM7HSukVUEW6Ucxr5ueaeHjT2CrwLc1xvoQo-sbh_K6F_gMl4fJyagIVte5duLSEGbKhb9v-t6hKEAgdP6ROvYr7uG3Mh0on_aLE5S4NcjMI5JTdvPJrso-qO8m8bA'
        sub1.device_id = '0000ffff-c97a-15d1-ffff-ffffef05ac4a'
        sub1.save()

        channel_name = 'NoExpire'
        ch = Channel.objects.create(name=channel_name, description="test for no expire", kind=PUBLIC)
        ch.owner = user
        ch.save()

        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = dict(sub_type=sub1.sub_type, device_id=sub1.device_id,
                    token=sub1.token)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.__setAuthToken(username=user.username, password="123")

        url = reverse('push-api:pushes-by-name', args=[channel_name])
        data = dict(body='Test non expire', message_type='text/plain')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)


    def test_push_with_target(self):
        """
        Test push something without passing expire
        """
        user = User.objects.create_user("usr_target", "usr_target@nowhere.com", "123")
        user.save()

        sub1 = Subscriber()
        sub1.sub_type = 'test'
        sub1.token = 'APA91bHTYr7cTsCPtCATdsywKfw1eWeBhuhyPM7HSukVUEW6Ucxr5ueaeHjT2CrwLc1xvoQo-sbh_K6F_gMl4fJyagIVte5duLSEGbKhb9v-t6hKEAgdP6ROvYr7uG3Mh0on_aLE5S4NcjMI5JTdvPJrso-qO8m8bA'
        sub1.device_id = '1111ffff-c97a-15d1-ffff-ffffef05ac4a'
        sub1.save()

        channel_name = 'Target'
        ch = Channel.objects.create(name=channel_name, description="test for no expire", kind=PUBLIC)
        ch.owner = user
        ch.save()

        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = dict(sub_type=sub1.sub_type, device_id=sub1.device_id,
                    token=sub1.token)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.__setAuthToken(username=user.username, password="123")

        url = reverse('push-api:pushes-by-name', args=[channel_name])
        data = dict(body='Test target', message_type='text/plain', target='iot_device')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)


    def test_push_not_inexistent_channel(self):
        url = reverse('channels-api:subscribe-channel-by-name', args=['NotExistChannel'])
        data = dict(sub_type='wp8', device_id='123456888',
                    token='123456')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_push_text_with_url(self):
        """
        Test push something without passing expire
        """
        user = User.objects.create_user("usr_url", "usr_url@nowhere.com", "123")
        user.save()

        sub1 = Subscriber()
        sub1.sub_type = 'test'
        sub1.token = 'BPA91bHTYr7cTsCPtCATdsywKfw1eWeBhuhyPM7HSukVUEW6Ucxr5ueaeHjT2CrwLc1xvoQo-sbh_K6F_gMl4fJyagIVte5duLSEGbKhb9v-t6hKEAgdP6ROvYr7uG3Mh0on_aLE5S4NcjMI5JTdvPJrso-qO8m8bA'
        sub1.device_id = '1000ffff-c97a-15d1-ffff-ffffef05ac4a'
        sub1.save()

        channel_name = 'UrlTest'
        ch = Channel.objects.create(name=channel_name, description="test for url in message", kind=PUBLIC)
        ch.owner = user
        ch.save()

        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = dict(sub_type=sub1.sub_type, device_id=sub1.device_id,
                    token=sub1.token)

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.__setAuthToken(username=user.username, password="123")

        url = reverse('push-api:pushes-by-name', args=[channel_name])
        data = dict(body='Test contains a url https://www.google.it and other text', message_type='text/plain')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["success"], True)

    def test_get_push_targets(self):
        url = reverse('target-api:target-list')
        response =  self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)



class API_SubscribersTestCase(APITestCase):
    """
    Test cases for Subscribers API calls
    """

    def setUp(self):
        settings.REDIS_DB = 15  # Db usato per i test
        SubscriberManager().flushdb()

    def test_subscribe_not_logged_device(self):
        print "--- subscribers ---"
        url = reverse('subscribers-api:subscribers-list')

        data = {
            u'token': u'APA91bGTpK3rxSwkXaH1negC7F4FWeNTRb-mBX9i6F8cPXq65NWaVfAdrrI4mtY8MLE7wUuyWnfGebgJeQ6U8zZGFjVy7FT5cfyPCg6L6mYoDGwmwC5-A5tnbCzitip78iMTjsQrQjjsZ3SmgeTrDuZloxXGwCpgiw',
            u'sub_type': u'android', u'name': u'UnitTest',
            u'device_id': u'ffffffff-c97a-15d1-ffff-ffffef05ac4a'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_subscrive_already_exist_device(self):
        url = reverse('subscribers-api:subscribers-list')
        data = {
            u'token': u'APA91bGTpK3rxSwkXaH1negC7F4FWeNTRb-mBX9i6F8cPXq65NWaVfAdrrI4mtY8MLE7wUuyWnfGebgJeQ6U8zZGFjVy7FT5cfyPCg6L6mYoDGwmwC5-A5tnbCzitip78iMTjsQrQjjsZ3SmgeTrDuZloxXGwCpgiw',
            u'sub_type': u'android', u'name': u'UnitTest',
            u'device_id': u'ffffffff-c97a-15d1-ffff-ffffef05ac4a'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        print "First device subscribe"
        ch1 = Channel.objects.create(name='SubCh1', description="", kind=PUBLIC)
        ch2 = Channel.objects.create(name='SubCh2', description="", kind=PUBLIC)

        SubscriberManager().subscribe('SubCh1', 'android', 'ffffffff-c97a-15d1-ffff-ffffef05ac4a',
                                      'APA91bGTpK3rxSwkXaH1negC7F4FWeNTRb-mBX9i6F8cPXq65NWaVfAdrrI4mtY8MLE7wUuyWnfGebgJeQ6U8zZGFjVy7FT5cfyPCg6L6mYoDGwmwC5-A5tnbCzitip78iMTjsQrQjjsZ3SmgeTrDuZloxXGwCpgiw')
        SubscriberManager().subscribe('SubCh2', 'android', 'ffffffff-c97a-15d1-ffff-ffffef05ac4a',
                                      'APA91bGTpK3rxSwkXaH1negC7F4FWeNTRb-mBX9i6F8cPXq65NWaVfAdrrI4mtY8MLE7wUuyWnfGebgJeQ6U8zZGFjVy7FT5cfyPCg6L6mYoDGwmwC5-A5tnbCzitip78iMTjsQrQjjsZ3SmgeTrDuZloxXGwCpgiw')

        data = {u'token': u'newtok',
                u'sub_type': u'android', u'name': u'UnitTest',
                u'device_id': u'ffffffff-c97a-15d1-ffff-ffffef05ac4a'}

        # Nuova registrazione del device post subscription di un paio di canali
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        newtok = SubscriberManager().get_subscription('SubCh1', 'android', 'ffffffff-c97a-15d1-ffff-ffffef05ac4a')
        self.assertEqual(newtok, 'newtok')

        newtok = SubscriberManager().get_subscription('SubCh2', 'android', 'ffffffff-c97a-15d1-ffff-ffffef05ac4a')
        self.assertEqual(newtok, 'newtok')



class API_ChannelSubscribersTestCase(APITestCase):
    """
    Test cases for Subscriptions API calls
    """

    def setUp(self):
        settings.REDIS_DB = 15  # Db usato per i test
        SubscriberManager().flushdb()

    def test_subscribe_not_logged_device(self):
        ch1 = Channel.objects.create(name='TestSubscriptions1', description="test for subscriptions 1", kind=PUBLIC)
        ch2 = Channel.objects.create(name='TestSubscriptions2', description="test for subscriptions 2", kind=PUBLIC)

        SubscriberManager().subscribe('TestSubscriptions1', 'ios', 'device1', 'token')
        SubscriberManager().subscribe('TestSubscriptions2', 'ios', 'device1', 'token')

        url = reverse('subscriptions-api:subsctiptions-list', args=['device1'])

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subscribe_requests(self):
        sub1 = Subscriber()
        sub1.sub_type = 'android'
        sub1.token = 'aabbccdd'
        sub1.device_id = 'devid_req'
        sub1.save()

        ch_owner = User.objects.create(first_name="Sample", last_name="User", email="sample@nowhere.org")

        Channel.objects.create(owner=ch_owner, name="Pub", description="", kind=PUBLIC, subscriptions=0)
        Channel.objects.create(owner=ch_owner, name="Pri", description="", kind=PRIVATE, subscriptions=0)

        url = reverse('channels-api:subscribe-channel-by-name', args=["Pub"])
        data = {'sub_type': 'android', 'device_id': 'devid_req', 'token': '2222'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('channels-api:subscribe-channel-by-name', args=["Pri"])
        data = {'sub_type': 'android', 'device_id': 'devid_req', 'token': '2222'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        url = reverse('subscriptions-api:requests-list', args=['devid_req'])

        response = self.client.get(url)
        self.assertTrue(len(response.data) == 2)
        self.assertTrue(any(x['channel']['kind'] == PUBLIC and x['channel']['name'] == 'Pub' for x in response.data))
        self.assertTrue(any(x['channel']['kind'] == PRIVATE and x['channel']['name'] == 'Pri' for x in response.data))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_subscribe_requests_only_pending(self):
        device_id = "devid_pen"
        channel_name = "Pri_Pen"
        token = 'aabbccdd'

        sub1 = Subscriber()
        sub1.sub_type = 'android'
        sub1.token = token
        sub1.device_id = device_id
        sub1.save()

        ch_owner = User.objects.create(first_name="Sample_pen", last_name="User_pen", email="sample_pen@nowhere.org")

        ch = Channel.objects.create(owner=ch_owner, name=channel_name, description="", kind=PRIVATE, subscriptions=0)

        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = {'sub_type': 'android', 'device_id': device_id, 'token': token}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        url = reverse('subscriptions-api:requests-list', args=[device_id])
        response = self.client.get(url)
        self.assertTrue(len(response.data) == 1)

        requests = ChannelSubscribeRequest.objects.filter(device_id=device_id)
        self.assertTrue(requests.count() == 1)
        change_request_status(requests[0], REJECTED)

        response = self.client.get(url)
        self.assertTrue(len(response.data) == 0)


    def test_subscribe_unicode_channelname(self):
        channel_name = "Kaffið"

        sub1 = Subscriber()
        sub1.sub_type = 'android'
        sub1.token = rnd_generator()
        sub1.device_id = rnd_generator()
        sub1.save()

        ch_owner = User.objects.create(first_name="Sample", last_name="User", email="sample@nowhere.org")

        Channel.objects.create(owner=ch_owner, name=channel_name, description="", kind=PUBLIC, subscriptions=0)

        url = reverse('channels-api:subscribe-channel-by-name', args=[channel_name])
        data = {'sub_type': sub1.sub_type , 'device_id': sub1.device_id, 'token': sub1.token }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        url = reverse('subscriptions-api:requests-list', args=['devid_req'])

        response = self.client.get(url)
        self.assertTrue(len(response.data) == 2)
        self.assertTrue(any(x['channel']['kind'] == PUBLIC and x['channel']['name'] == channel_name for x in response.data))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

class API_MessagesTestCase(APITestCase):
    """
    Test cases for Subscribers API calls
    """

    def setUp(self):
        settings.REDIS_DB = 15  # Db usato per i test
        SubscriberManager().flushdb()

    def test_get_message_by_id(self):
        ch = Channel.objects.create(name="ChannelWithMsg", description="test for messages", kind=PUBLIC)
        msg = ChannelMsg.objects.create(message_type="text/plain", channel=ch, body="bla bla bla blu",
                                        expire=datetime.utcnow() + timedelta(days=5))

        url = reverse('messages-api:messages-by-id', args=[msg.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_message_by_id_fail(self):
        url = reverse('messages-api:messages-by-id', args=[100])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_my_messages(self):
        test_device = 'dev_id'

        ch1 = Channel.objects.create(name="SubCha1", description="", kind=PUBLIC)
        ch2 = Channel.objects.create(name="SubCha2", description="", kind=PUBLIC)

        SubscriberManager().subscribe("SubCha1", 'ios', test_device, 'token')
        SubscriberManager().subscribe("SubCha2", 'ios', test_device, 'token')

        msg1 = ChannelMsg(channel=ch1)
        msg1.body = "aaa"
        msg1.message_type = "text/plain"
        msg1.expire = datetime.utcnow() + timedelta(days=5)
        msg1.save()

        msg2 = ChannelMsg(channel=ch2)
        msg2.body = "bbbb"
        msg2.message_type = "text/plain"
        msg2.expire = datetime.utcnow() + timedelta(days=3)
        msg2.save()

        msg_expired = ChannelMsg(channel=ch2)
        msg_expired.body = "cccc"
        msg_expired.message_type = "text/plain"
        msg_expired.expire = datetime.utcnow() + timedelta(days=-3)
        msg_expired.save()

        url = reverse('messages-api:messages-by-owner', args=[test_device])

        response = self.client.get(url)
        print response.data
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

class API_FeedbackTestCase(APITestCase):
    """
    Test cases for FeedbackService API calls
    """

    def setUp(self):
        settings.REDIS_DB = 15  # Db usato per i test
        SubscriberManager().flushdb()

    def test_get_feedback_message(self):
        test_channel = "ChFeedback"
        ch1 = Channel.objects.create(name=test_channel, description="", kind=PUBLIC)
        
        msg1 = ChannelMsg(channel=ch1)
        msg1.body = "Test Feedback"
        msg1.message_type = "text/plain"
        msg1.expire = datetime.utcnow() + timedelta(days=5)
        msg1.save()
        
        url = reverse('feedback-api:feedback-many-messages')

        data = {'device_id': '12345', 'messages_id': [msg1.id]}

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
