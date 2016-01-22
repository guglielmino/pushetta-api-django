# coding=utf-8

# Progetto: Pushetta API 
# Serializer dei DTO 

from drf_compound_fields.fields import ListField

from rest_framework import serializers
from rest_framework.pagination import PaginationSerializer
from rest_framework.serializers import ValidationError
from django.contrib.auth.models import User

from core.models import Channel, ChannelMsg, Subscriber, ChannelSubscribeRequest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email', )


class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('id', 'name', 'image', 'description', 'kind', )


class MinimalChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Channel
        fields = ('id', 'name', 'image', )


class PaginatedChannelSerializer(PaginationSerializer):
    start_index = serializers.SerializerMethodField('get_start_index')
    end_index = serializers.SerializerMethodField('get_end_index')
    num_pages = serializers.Field(source='paginator.num_pages')

    class Meta:
        object_serializer_class = ChannelSerializer

    def get_start_index(self, page):
        return page.start_index()

    def get_end_index(self, page):
        return page.end_index()

    def get_curr_page(self, page):
        return page.number


class ChannelMsgSerializer(serializers.ModelSerializer):
    channel = MinimalChannelSerializer()

    class Meta:
        model = ChannelMsg
        fields = ('id', 'body', 'date_created', 'expire', 'channel', 'preview_url', )


class SubscriberModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ('device_id', 'token', 'sub_type', 'name', )


class SubscriberSerializer(serializers.Serializer):
    sub_type = serializers.CharField(max_length=100)  # iOS, Android, ...
    device_id = serializers.CharField(max_length=200)
    token = serializers.CharField(max_length=500)
    name = serializers.CharField(max_length=250)


class ChannelSubscriptionSerializer(serializers.Serializer):
    sub_type = serializers.CharField(max_length=100)  # iOS, Android, ...
    device_id = serializers.CharField(max_length=200)
    token = serializers.CharField(max_length=500)


class PushMessageSerializer(serializers.Serializer):
    message_type = serializers.CharField(max_length=100)
    body = serializers.CharField(max_length=500)
    expire = serializers.DateField(required=False)
    target = serializers.CharField(max_length=20, required=False)


class PublisherSerializer(serializers.Serializer):
    dummy = serializers.CharField(max_length=100)


class FeedbackSerializer(serializers.Serializer):
    device_id = serializers.CharField(max_length=200)
    messages_id = ListField(serializers.IntegerField())


class PushResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    error_code = serializers.CharField(max_length=200)


class CheckVersionSerializer(serializers.Serializer):
    need_update = serializers.BooleanField()
    message = serializers.CharField(max_length=200)


class ChannelSubscribeRequestSerializer(serializers.ModelSerializer):
    channel = ChannelSerializer()

    class Meta:
        model = ChannelSubscribeRequest
        fields = ('channel', 'status')


class TargetSerializer(serializers.WritableField):

    def from_native(self, data):
        if isinstance(data, list):
            return data
        else:
            msg = self.error_messages['invalid']
            raise ValidationError(msg)

    def to_native(self, obj):
        return obj