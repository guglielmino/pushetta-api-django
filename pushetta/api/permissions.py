# coding=utf-8

# Progetto: Pushetta API 
# Permission custom

from rest_framework import permissions


class IsDeviceCallAuthorized(permissions.BasePermission):
    """
    Custom permission to check if a device can invoke a API method.
    It check a custom HTTP Header for operations made from devices (it check a signature based on seed delivered with push notification)
    Custom HTTP header is X-Auth-Token
    """

    def has_permission(self, request, view):
        if 'HTTP_X_AUTH_TOKEN' in request.META:
            req_custom_header = request.META['HTTP_X_AUTH_TOKEN']
            print req_custom_header

        return True

    def has_object_permission(self, request, view, obj):
        return True


class IsChannelOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_permission(self, request, view):
        print "IsChannelOwner has_permission"
        return True

    def has_object_permission(self, request, view, obj):
        print "IsChannelOwner has_object_permission"
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Instance must have an attribute named `owner`.
        return obj.owner == request.user