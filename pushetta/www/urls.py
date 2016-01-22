# coding=utf-8

# Progetto: Pushetta API 
# Definizione delle Url per la API

from django.conf.urls import patterns, url, include
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from dispatcher_view import ChannelSubscriberDispatcher, AndroidSubscribe, iOSSubscribe, SafariSubscribe, \
    ChromeSubscribe
from my_views import MyDashboardView, MyChannelsView, ChannelCreate, ChannelSearchView, ApproveRequestsView, \
    UpdateChannelView

from safari_views import SafariPushService, SafariPackageDownloadService, SafariLogService
from browser_views import WebPushRegistration

from upload_views import multiuploader, multiuploader_delete

from django.views.decorators.csrf import csrf_exempt

#  Funzionalità disponibili solo all'utente loggato
privatearea_urls = patterns('',
                            url(r'^dashboard/$', login_required(MyDashboardView.as_view()),
                                name="pushetta-dashboard"),
                            url(r'^channels/$', login_required(MyChannelsView.as_view()), name="my-channels"),
                            url(r'^channels/create/$', login_required(ChannelCreate.as_view()),   name="my-channelcreate"),

                            url(r'^channels/update-props/$', login_required(UpdateChannelView.as_view()), name="my-channelupdate-props"),

                            url(r'^channels/(?P<channel_name>[\w|\W]+)/push/$',
                                login_required(MyChannelsView.as_view()),
                                name="my-channel-pushmessage"),
                            url(r'^channels/(?P<channel_name>[\w|\W]+)/$', login_required(MyChannelsView.as_view()),
                                name="my-channelview"),
                            url(r'^requests/approve/$', login_required(ApproveRequestsView.as_view()),
                                name="my-approve-requests"),

)

# Url per la gestione della sottoscrizione ai Canali con gestione
# del device di provenienza (Android, iOs, Wp, ...)
channel_subscription_urls = patterns('',
                                     url(r'^dispatch/(?P<channel_name>[\w|\W]+)/$',
                                         ChannelSubscriberDispatcher.as_view(), name="channel-subscription-dispatcher"),
                                     url(r'^android/(?P<channel_name>[\w|\W]+)/$',
                                         AndroidSubscribe.as_view(),
                                         name="android-subscribe"),
                                     url(r'^ios/(?P<channel_name>[\w|\W]+)/$', iOSSubscribe.as_view(),
                                         name="ios-subscribe"),
                                     url(r'^safari/(?P<channel_name>[\w|\W]+)/$',
                                         login_required(SafariSubscribe.as_view()),
                                         name="safari-subscribe"),
                                     url(r'^chrome/(?P<channel_name>[\w|\W]+)/$',
                                         login_required(ChromeSubscribe.as_view()),
                                         name="chrome-subscribe"),

)

file_uploads_urls = patterns('',
                             url(r'^delete/(\d+)/$', multiuploader_delete, name="upload-delete"),
                             url(r'^multi/$', multiuploader, name="upload-file"),
)

# Url per la gestione della meccanica per il push to browser Safari
safari_urls = patterns('',
                       url(r'^/devices/(?P<deviceToken>[\w|\W]+)/registrations/web.com.pushetta$',
                           csrf_exempt(SafariPushService.as_view()), name='safari-token-register'),
                       url(r'^/pushPackages/web.com.pushetta$', csrf_exempt(SafariPackageDownloadService.as_view()),
                           name='safari-package-download'),
                       url(r'^/log', csrf_exempt(SafariLogService.as_view()), name='safari-log'),
)

browser_urls = patterns('',
                        # Endpoint per la registrazione anonima del solo device
                        url(r'^register/device$', csrf_exempt(WebPushRegistration.as_view()),
                            name='browser-registration-device'),

                        url(r'^register/(?P<device_id>[\w|\W]+)/(?P<channel_name>[\w|\W]+)/$',
                            login_required(csrf_exempt(WebPushRegistration.as_view())),
                            name='browser-get-registration'),

                        url(r'^register$', login_required(csrf_exempt(WebPushRegistration.as_view())),
                            name='browser-registration'),

)

urlpatterns = patterns('',
                       url(r'^$', TemplateView.as_view(template_name="index.html"), name="pushetta-index"),
                       url(r'^cookie_policy/$', TemplateView.as_view(template_name="cookie_policy.html"), name="cookie_policy"),
                       url(r'^apps/$', TemplateView.as_view(template_name="apps.html"), name="pushetta-apps"),
                       url(r'^search/$', ChannelSearchView.as_view(), name="site-channel-search"),
                       url(r'^my/', include(privatearea_urls)),
                       url(r'^pushetta-search/$', ChannelSearchView.as_view(),
                           name="pushetta-search"),
                       url(r'^pushetta-api/', TemplateView.as_view(template_name="api-docs.html"),
                           name="pushetta-api-doc"),
                       url(r'^pushetta-docs/$', TemplateView.as_view(template_name="docs.html"), name="pushetta-docs"),
                       url(r'^pushetta-downloads/$', TemplateView.as_view(template_name="downloads.html"),
                           name="pushetta-downloads"),

                       # API per l'integrazione push Safari
                       url(r'^safari/v1', include(safari_urls)),

                       # API per la gestione dei token acquisiti dal browser per le notifiche Push
                       url(r'^browser/', include(browser_urls)),

                       # Login, registrazione, ... con allauth
                       url(r'^accounts/', include('allauth.urls')),

                       url(r'subs/', include(channel_subscription_urls)),
                       url(r'resource/', include(file_uploads_urls)),

                       url(r'^robots\.txt$',
                           TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),

)

