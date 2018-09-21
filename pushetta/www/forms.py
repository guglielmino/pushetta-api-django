# coding=utf-8

# Progetto: Pushetta API 
# Definizione delle form usate nel progetto

from django.forms import ModelForm
from django import forms

from core.models import Channel, ChannelMsg


class ChannelForm(ModelForm):
    class Meta:
        model = Channel
        fields = ['name', 'image', 'description', 'kind', 'hidden']

        widgets = {
            'name': forms.TextInput(attrs={
                                            'class': 'span6',
                                            'placeholder': 'Choose a name for Your channel'
                                    }),
            'description': forms.Textarea(attrs={
                                                    'class': 'span6',
                                                    'rows': 4,
                                                    'placeholder': 'Give a brief description of the meaning of Your channel'
                                                  }),
            'image': forms.HiddenInput()
        }

