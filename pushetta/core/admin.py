# coding=utf-8

# Progetto: Pushetta API 
# Estensioni della Admin

from django.contrib import admin
from models import Channel, ChannelMsg, Subscriber, StoredImage

class ChannelAdmin(admin.ModelAdmin):
   list_display = ('name', 'description', 'subscriptions', 'date_created',)

class ChannelMsgAdmin(admin.ModelAdmin):
   list_display = ('date_created', )

class SubscriberAdmin(admin.ModelAdmin):
   list_display = ('sub_type', 'device_id', 'token', 'enabled', 'name', )
      
admin.site.register(Channel, ChannelAdmin) 
admin.site.register(ChannelMsg, ChannelMsgAdmin) 
admin.site.register(Subscriber, SubscriberAdmin) 

