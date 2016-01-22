# coding=utf-8

# Progetto: Pushetta API 
# Custom tag con la definizione dei link per il download delle App dai vari store

from django import template

register = template.Library()

store_links = {'android': "/apps",
               'ios': "/apps",
               'wp8': "/apps"}


@register.simple_tag(takes_context=True)
def storelink(context, platform, **kwargs):
    return_value = ""
    if platform in store_links:
        return_value = store_links[platform]
    return return_value
