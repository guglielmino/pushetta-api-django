# coding=utf-8

# Progetto: Pushetta Site 
# Calss view per la gestione del dispatcher su device mobile

import logging

logger = logging.getLogger(__name__)

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View
from django.core.urlresolvers import reverse

from django.shortcuts import render_to_response, get_object_or_404


from django.template import RequestContext
from core.models import Channel

from user_agents import parse


class ChannelSubscriberDispatcher(View):
    def get(self, request, channel_name=None):
        ua_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(ua_string)

        logger.info(user_agent.browser.family)

        if user_agent.os.family == 'Android':
            return HttpResponseRedirect(reverse('android-subscribe', args=[channel_name]))
        elif user_agent.os.family == "iOS":
            return HttpResponseRedirect(reverse('ios-subscribe', args=[channel_name]))

        channel = get_object_or_404(Channel, name=channel_name)
        return render_to_response("channel-dispatcher.html", {
                                                                 'channel': channel,
                                                                 'browser' : user_agent.browser.family,
                                                             },
                                  context_instance=RequestContext(request))




    # Identificazione del mobile device per reagire nel modo corretto con il dispatcher
    # Può tornare : iphone, ipad, android, blackberry, wp7, wp8 o wp (windows mobile generico)
    def __mobile(self, request):

        device = ''

        ua = request.META.get('HTTP_USER_AGENT', '').lower()

        if ua.find("iphone") > 0:
            device = "iphone"  # + re.search("iphone os (\d)", ua).groups(0)[0]

        if ua.find("ipad") > 0:
            device = "ipad"

        if ua.find("android") > 0:
            device = "android"  # + re.search("android (\d\.\d)", ua).groups(0)[0].translate(None, '.')

        if ua.find("blackberry") > 0:
            device = "blackberry"

        if ua.find("windows phone os 7") > 0:
            device = "wp7"
        elif ua.find("windows phone 8") > 0:
            device = "wp8"
        elif ua.find("iemobile") > 0:
            device = "wp"

        if not device:  # either desktop, or something we don't care about.
            device = "baseline"

        return device

class AndroidSubscribe(View):

    def get(self, request, channel_name=None):
        channel = None
        try:
            channel = Channel.objects.get(name=channel_name)
        except Channel.DoesNotExist:
            pass

        return render_to_response("android-subscribe.html", {'channel': channel},
                                  context_instance=RequestContext(request))

class iOSSubscribe(View):

    def get(self, request, channel_name=None):
        channel = None
        try:
            channel = Channel.objects.get(name=channel_name)
        except Channel.DoesNotExist:
            pass

        return render_to_response("ios-subscribe.html", {'channel': channel},
                                  context_instance=RequestContext(request))
                                  
class SafariSubscribe(View):

    def get(self, request, channel_name=None):
        channel = None
        try:
            channel = Channel.objects.get(name=channel_name)
        except Channel.DoesNotExist:
            pass

        return render_to_response("safari-subscribe.html", {'channel': channel},
                                  context_instance=RequestContext(request))

class ChromeSubscribe(View):

    def get(self, request, channel_name=None):
        channel = None
        try:
            channel = Channel.objects.get(name=channel_name)
        except Channel.DoesNotExist:
            pass

        return render_to_response("chrome-subscribe.html", {'channel': channel},
                                  context_instance=RequestContext(request))
