# coding=utf-8

# Progetto: Pushetta Core
# Varie funzioni di utilità usate nel progetto

from django.utils import six
from django.conf import settings


def custom_get_identifier(obj_or_string):
    """
    Get an unique identifier for the object or a string representing the
    object.

    If not overridden, uses <app_label>.<object_name>.<pk>.
    """
    if isinstance(obj_or_string, six.string_types):
        if not IDENTIFIER_REGEX.match(obj_or_string):
            raise AttributeError(u"Provided string '%s' is not a valid identifier." % obj_or_string)

        return obj_or_string

    return u"%s" % (obj_or_string._get_pk_val())
