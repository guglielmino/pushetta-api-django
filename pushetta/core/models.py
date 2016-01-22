# coding=utf-8

# Progetto: Pushetta API 
# Models 

import os
from uuid import uuid4

from datetime import datetime
from django.contrib.auth.models import User
from django.db import models

from django.db.models import signals


from django.core.urlresolvers import reverse
from django.utils.deconstruct import deconstructible

from taggit.managers import TaggableManager
from fileds_validators import isalphavalidator

'''
Extension of standard Django user

class User(AbstractUser):
   pass
'''

PRIVATE = 0
PUBLIC = 1
AD = 2
CHANNEL_CHOICES = (
    (PRIVATE, 'Private'),
    (PUBLIC, 'Public'),
)

# Funzione passata all'attributo upload_to per rinominare dinamicamente
# il file uploadato
@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

path_and_rename = PathAndRename("channel_media/")


class Channel(models.Model):
    """
    Il canale
    """
    owner = models.ForeignKey(User, null=True, related_name='channels')
    name = models.CharField(max_length=20, db_index=True, unique=True, validators=[isalphavalidator])
    image = models.URLField()
    description = models.CharField(max_length=255, validators=[isalphavalidator])
    kind = models.IntegerField(default=1, choices=CHANNEL_CHOICES)
    hidden = models.BooleanField(default=False)

    tags = TaggableManager()

    subscriptions = models.IntegerField(default=0)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('my-channelview', kwargs={'channel_name': self.name})

    class Meta:
        ordering = ['-date_created']


class ChannelMsg(models.Model):
    """
    Messaggio pushato associato al canale storato
    """
    channel = models.ForeignKey(Channel, related_name='messages')
    message_type = models.CharField(max_length=50, default='text/plain')
    body = models.CharField(max_length=500)
    expire = models.DateTimeField()

    # Link alla preview dell'eventuale url presente nel testo  (se più di una l'ultima)
    preview_url = models.URLField(null=True, blank=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_created']


class Subscriber(models.Model):
    """
    Model per i subscriber storati su db
    """
    sub_type = models.CharField(max_length=100, default='Unknown')  # Tipo di subscriber (iOS, Android, WP8, ...)

    device_id = models.CharField(max_length=100, db_index=True, primary_key=True)  # Identificatore univoco del device

    token = models.CharField(max_length=500)
    enabled = models.BooleanField(default=True)

    name = models.CharField(max_length=250)  # Nome del subscriber per permetterne la gestione all'utente

    sandbox = models.BooleanField(default=False)

    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_modified = models.DateTimeField(auto_now=True)


class StoredImage(models.Model):
    """
    Model per le immagini uploadate
    """
    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.FileField(upload_to=path_and_rename)

    def __unicode__(self):
        return self.image.name


PENDING = 0
ACCEPTED = 1
REJECTED = 2
SUBSCRIBE_REQ_STATUS = (
    (PENDING, 'Pending'),
    (ACCEPTED, 'Accepted'),
    (REJECTED, 'Rejected'),
)

# TODO: device_id e channel devono fare da chiave
class ChannelSubscribeRequest(models.Model):
    """
    Model per le richieste di subscribe
    """

    device_id = models.CharField(max_length=100, db_index=True)
    channel = models.ForeignKey(Channel, related_name='requests')

    status = models.IntegerField(default=0, choices=SUBSCRIBE_REQ_STATUS)

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    @property
    def subscriber(self):
        return Subscriber.objects.get(device_id=self.device_id)
