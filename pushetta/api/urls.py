# coding=utf-8

# Progetto: Pushetta API 
# Definizione delle Url per la API

from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required

from api.channels_sl import ChannelsList, ChannelSearch, ChannelSubscription, ChannelSuggestion, ChannelUnSubscription
from api.publisher_sl import PublisherList
from api.pushes_sl import PushList, TargetList
from api.subscriber_sl import SubscriberList, SubcriptionsList, DeviceSubscriptionsRequests
from api.messages_sl import MessageList
from api.feedback_sl import FeedbackService
from api.crashes_sl import CrashLogService
from api.sys_sl import CheckVersion


channel_urls = [
   url(r'^/subscription/(?P<name>[\w|\W]+)/(?P<sub_type>[\w|\W]+)/(?P<device_id>[\w|\W]+)/$', ChannelUnSubscription.as_view(), name='unsubscribe-channel-by-name'),
   url(r'^/subscription/(?P<name>[\w|\W]+)/$', ChannelSubscription.as_view(),name='subscribe-channel-by-name'),
   url(r'^/$', ChannelsList.as_view(), name='channel-list'),
   url(r'^/search/$', ChannelSearch.as_view(), name='channel-search'),
   url(r'^/suggestions/(?P<device_id>[\w|\W]+)/$', ChannelSuggestion.as_view(), name='channel-suggestions')
]

publisher_urls = [
   url(r'^/channels/(?P<name>[\w|\W]+)/$', PublisherList.as_view(), name='publishers-by-name'),
]

messages_urls = [
   url(r'^/my/(?P<device_id>[\w|\W]+)/$', MessageList.as_view(), name='messages-by-owner'),
   url(r'^/(?P<message_id>[\w|\W]+)/$', MessageList.as_view(), name='messages-by-id'),
]

pushes_urls = [
   url(r'^/(?P<name>[\w|\W]+)/$', PushList.as_view(), name='pushes-by-name'),
]

targets_urls = [
   url(r'^/$', TargetList.as_view(), name='target-list'),
]

subscribers_urls = [
   url(r'^/$', SubscriberList.as_view(), name='subscribers-list'),
]

subscriptions_urls = [
   url(r'^/requests/(?P<deviceId>[\w|\W]+)/$', DeviceSubscriptionsRequests.as_view(), name='requests-list'),
   url(r'^/(?P<deviceId>[\w|\W]+)/$', SubcriptionsList.as_view(), name='subsctiptions-list'),
]

feedback_urls = [
   
   url(r'^/(?P<message_id>[\w|\W]+)/$', FeedbackService.as_view(), name='feedback-one-message'),
   url(r'^/$', FeedbackService.as_view(), name='feedback-many-messages'),
]

android_urls = [
   url(r'^/crashlog/', CrashLogService.as_view(), name='crashlog'),
]

sys_urls =  [
   url(r'^/version/$', CheckVersion.as_view(), name='sys-app-version'),
]



urlpatterns = [
   # Autenticazione con AuthToken del django rest framework
   url(r'^auth/', 'rest_framework.authtoken.views.obtain_auth_token', name="auth-token"),

   url(r'^sys', include(sys_urls, namespace="sys-api")),

   url(r'^channels', include(channel_urls, namespace="channels-api")),
   url(r'^publisher', include(publisher_urls, namespace="publisher-api")),
   url(r'^pushes', include(pushes_urls, namespace="push-api")),
   url(r'^targets', include(targets_urls, namespace="target-api")),

   # NOTA :Verificare il porting del get di messages su questo
   url(r'^messages', include(messages_urls, namespace="messages-api")),
   url(r'^subscribers', include(subscribers_urls, namespace="subscribers-api")),
   url(r'^subscriptions', include(subscriptions_urls, namespace="subscriptions-api")),
   url(r'^feedback', include(feedback_urls, namespace="feedback-api")),
                       
   url(r'^android/crashlog/', include(android_urls, namespace="android-api")),
]