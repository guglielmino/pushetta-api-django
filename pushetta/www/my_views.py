# Progetto: Pushetta Site 
# Class view per la gestione delle view dell'area privata (/my)

# -*- coding: utf-8 -*-
from __future__ import unicode_literals


import json

from datetime import datetime
from dateutil.relativedelta import relativedelta

from django.http import Http404
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from django.views.generic.edit import DeletionMixin
from django.views.generic.edit import CreateView
from django.template import RequestContext
from django.shortcuts import render_to_response
from haystack.query import SearchQuerySet
from haystack.inputs import Clean

from core.subscriber_manager import SubscriberManager

from core.models import Channel, Subscriber, ChannelMsg, ChannelSubscribeRequest
from core.models import ACCEPTED, REJECTED, PRIVATE, PUBLIC
from forms import ChannelForm

from core.services import send_push_message, search_public_channels, get_suggested_channels, change_request_status

# Nota: a tendere va rimosso con la gestione client del CSRF
from django.views.decorators.csrf import csrf_exempt

from rest_framework.authtoken.models import Token
from rest_framework_jwt.settings import api_settings


class MyDashboardView(View):
    def get(self, request):
        owner_channels = Channel.objects.filter(owner=request.user)

        auth_token = None
        try:
            auth_token = Token.objects.get(user=request.user)

        except Token.DoesNotExist:
            auth_token = Token.objects.create(user=request.user)

        subscribers_tokens = []
        subscribers = []
        chan_subscribers = []
        for channel in owner_channels:
            chan_subscribers = SubscriberManager().get_all_subscribers(channel.name)
            subscribers_tokens.append(chan_subscribers)
            subscribers.append(Subscriber.objects.filter(token__in=chan_subscribers))

        messages_count = ChannelMsg.objects.filter(channel__in=owner_channels).count()

        return render_to_response('dashboard.html',
                                  dict(
                                      apikey=auth_token.key if auth_token else "No token",
                                      owner_channels_count=len(owner_channels),
                                      latest_channels=owner_channels[:5],
                                      subscribers_count=len(chan_subscribers),
                                      messages_count=messages_count,
                                      subscribers=subscribers[:5]
                                  ),
                                  context_instance=RequestContext(request)
        )


class MyChannelsView(View, DeletionMixin):
    """
    Gestisce la lista o la singola view
    """

    def get(self, request, channel_name=None):
        if channel_name is None:
            user_channels = request.user.channels

            return render_to_response('my_channels.html',
                                      dict(user_channels=user_channels.all()),
                                      context_instance=RequestContext(request)
            )
        else:
            channels = Channel.objects.filter(owner=request.user).filter(name=channel_name)
            tokens = SubscriberManager().get_all_subscribers(channel_name)[:10]
            subscribers = Subscriber.objects.filter(token__in=tokens)
            requests = ChannelSubscribeRequest.objects.filter(channel=channels[0])

            return render_to_response('my_channel-view.html',
                                      {
                                          'channel': channels[0],
                                          'subscribers': subscribers,
                                          'requests': requests,
                                      },
                                      context_instance=RequestContext(request)
            )

    def post(self, request, channel_name=None):
        if request.is_ajax:
            try:
                channel = Channel.objects.get(name=channel_name)
            except Channel.DoesNotExist:
                return Http404()

            body = request.POST['body']
            expire = datetime.today() + relativedelta(months=1)  # Default 1 mese
            response = send_push_message(channel, 'text/plain', body, expire)

            return HttpResponse(json.dumps(response.__dict__))
        else:
            return HttpResponseBadRequest()

    def delete(self, request, channel_name=None):
        if channel_name:
            channel = Channel.objects.filter(owner=request.user).filter(name=channel_name)
            if channel:
                channel.delete()
                response_data = json.dumps(dict(Success=True))

                return HttpResponse(response_data, content_type='application/json')
        return HttpResponseBadRequest("Can't delete Channel")


class ChannelSearchView(View):
    def get(self, request):
        q = request.GET.get('term', '')

        if request.is_ajax():
            page = request.GET.get('page', None)
            sqs = search_public_channels(q)

            return HttpResponse(json.dumps([dict(name=q.name, image=q.image, kind=q.kind) for q in sqs]),
                                content_type="application/json")
        else:
            channels = []
            if q:
                channels = search_public_channels(q)
            else:

                channels = get_suggested_channels()
            return render_to_response('search.html',
                                      {
                                          'suggested': channels,
                                      },
                                      context_instance=RequestContext(request)
            )

        return HttpResponse()


class ChannelCreate(CreateView):
    template_name = "my_channel-add.html"
    # model = Channel
    form_class = ChannelForm
    fields = ['name', 'image', 'description', 'kind', 'hidden']


    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.save()
        return super(ChannelCreate, self).form_valid(form)


class ApproveRequestsView(View):
    """
    Metodo Ajax per la gestione della richiesta di approvazione/negazione
    della subscription ad un canale privato
    """

    def post(self, request):
        if request.is_ajax():
            sub_req_id = request.POST['sub_req_id']
            new_status = request.POST['new_status']

            statuses_mapper = {"APPROVE": ACCEPTED, "REJECT": REJECTED}

            subscribe_request = ChannelSubscribeRequest.objects.get(id=sub_req_id)

            change_request_status(subscribe_request, statuses_mapper[new_status])

            return HttpResponse(json.dumps(True),
                                content_type="application/json")

        return HttpResponseBadRequest()


class UpdateChannelView(View):
    """
    Metodo Ajax per la gestione dell'aggiornamento properties del canale
    """

    def post(self, request):
        if request.is_ajax():
            channel_id = request.POST['channel_id']
            trues = ['true', '1', 't', 'y', 'yes', 'True']
            hidden = request.POST['hidden'] in trues
            public = request.POST['public'] in trues

            res = True
            try:
                channel = Channel.objects.get(id=channel_id)
                channel.hidden = hidden
                channel.kind = PUBLIC if public else PRIVATE
                channel.save()
            except Channel.DoesNotExist:
                res = False

            return HttpResponse(json.dumps(res),
                                content_type="application/json")

        return HttpResponseBadRequest()