# coding=utf-8

# Progetto: Pushetta API 
# Definizione dei validators custom per i model fileds

from django.core.validators import RegexValidator

# '^[\w]*$'
isalphavalidator = RegexValidator(r'[a-zA-Z0-9_\-\s].*',
                             message='invalid characters in field',
                             code='Invalid value')