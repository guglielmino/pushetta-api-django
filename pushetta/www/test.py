# coding=utf-8

# Progetto: Pushetta Site 
# Test delle view del progetto

from django.test import TestCase
from django.core.urlresolvers import reverse
from core.models import Subscriber, Channel, User
from core.services import *
import json

class TestBrowserViews(TestCase):

    def setUp(self):
        settings.REDIS_DB = 15  # Db usato per i test
        self.manager = SubscriberManager()
        self.manager.flushdb()

    def test_call_get(self):
        '''
        Test check if a device is registered to a channel
        '''

        u = User()
        u.username = "sample_un"
        u.first_name = "Sample_un"
        u.email = "sample_un@nowhere.org"
        u.set_password("123")
        u.save()

        ch1 = Channel()

        ch1.owner = u
        ch1.name = "GetSub"
        ch1.image = 'http://www.google.com'
        ch1.description = "A channel description"
        ch1.kind = PUBLIC
        ch1.hidden = False
        ch1.subscriptions = 0

        ch1.save()

        sub1 = Subscriber()
        sub1.sub_type = 'type2'
        sub1.token = 'token2'
        sub1.device_id = 'devid4'
        sub1.save()


        resp = ask_subscribe_channel(ch1, 'devid4')

        self.assertEqual(resp, SubscribeResponse.SUBSCRIBED)
        test_user = User.objects.create_superuser('test_user', 'test_user@nowhere.org', 'password')
        self.client.login(username='test_user', password='password')

        response = self.client.get(reverse('browser-get-registration', kwargs={'device_id': 'devid4', 'channel_name' : 'GetSub'}) )
        
        self.assertTrue(response.status_code, 200)

    def test_call_register_channel(self):
        '''
        Test registration to a channel
        '''

        u = User()
        u.username = "sample_post"
        u.first_name = "sample_post"
        u.email = "sample_post@nowhere.org"
        u.set_password("123")
        u.save()

        ch1 = Channel()

        ch1.owner = u
        ch1.name = "PostSub"
        ch1.image = 'http://www.google.com'
        ch1.description = "A channel description"
        ch1.kind = PUBLIC
        ch1.hidden = False
        ch1.subscriptions = 0

        ch1.save()

        sub1 = Subscriber()
        sub1.sub_type = 'type2'
        sub1.token = 'token2'
        sub1.device_id = 'devid5'
        sub1.save()


        resp = ask_subscribe_channel(ch1, sub1.device_id)

        self.assertEqual(resp, SubscribeResponse.SUBSCRIBED)
        test_user = User.objects.create_superuser('test_user', 'test_user@nowhere.org', 'password')
        self.client.login(username='test_user', password='password')

        data = {
                'channel' : ch1.name,
                'token' : sub1.token,
                'browser' : 'chrome',
                'device_id' : sub1.device_id
        }

        response = self.client.post(reverse('browser-registration'), json.dumps(data), sub1.token)

        self.assertTrue(response.status_code, 200)

    def test_call_delete(self):
        '''
        Test deleting of a registration of a device from a channel
        '''

        u = User()
        u.username = "sample_del"
        u.first_name = "sample_del"
        u.email = "sample_del@nowhere.org"
        u.set_password("123")
        u.save()

        ch1 = Channel()

        ch1.owner = u
        ch1.name = "DelSub"
        ch1.image = 'http://www.google.com'
        ch1.description = "A channel description"
        ch1.kind = PUBLIC
        ch1.hidden = False
        ch1.subscriptions = 0

        ch1.save()

        sub1 = Subscriber()
        sub1.sub_type = 'type2'
        sub1.token = 'token2'
        sub1.device_id = 'devid6'
        sub1.save()


        resp = ask_subscribe_channel(ch1, sub1.device_id)

        self.assertEqual(resp, SubscribeResponse.SUBSCRIBED)
        test_user = User.objects.create_superuser('test_user', 'test_user@nowhere.org', 'password')
        self.client.login(username='test_user', password='password')

        response = self.client.delete(reverse('browser-get-registration', kwargs={'device_id': sub1.device_id,
                                                                       'channel_name' : ch1.name}))

        self.assertEqual(response.status_code, 200)

        channels = SubscriberManager().get_device_subscriptions(sub1.device_id)
        sub_channel = next((x for x in channels if x == ch1.name.lower()), None)

        self.assertIsNone(sub_channel)
        
        
        
    
    def test_call_register_device(self):
        '''
        Test a registration without passing channel name (only device will be registered)
        '''

        test_user = User.objects.create_superuser('test_user_dev', 'test_user@nowhere.org', 'password')
        self.client.login(username='test_user_dev', password='password')

        data = {                
                'token' : 'sample_token',
                'browser' : 'chrome',
                'device_id' : "123-567-89"
        }

        response = self.client.post(reverse('browser-registration'), json.dumps(data), data["token"])

        self.assertTrue(response.status_code, 200)
        sub = Subscriber.objects.get(token=data["token"])
        self.assertEqual(data["device_id"], sub.device_id)


