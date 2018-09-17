# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from PIL import Image

from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from core.models import StoredImage
from django.core.files.uploadedfile import UploadedFile


import json

# Nota: a tendere va rimosso con la gestione client del CSRF
from django.views.decorators.csrf import csrf_exempt

import logging

log = logging


@csrf_exempt
def multiuploader_delete(request, pk):
    """
    View for deleting photos with multiuploader AJAX plugin.
    made from api on:
    https://github.com/blueimp/jQuery-File-Upload
    """
    if request.method == 'POST':
        log.info('Called delete image. Photo id=' + str(pk))
        image = get_object_or_404(Image, pk=pk)
        image.delete()
        log.info('DONE. Deleted photo id=' + str(pk))
        return HttpResponse(str(pk))
    else:
        log.info('Recieved not POST request todelete image view')
        return HttpResponseBadRequest('Only POST accepted')


@csrf_exempt
def multiuploader(request):
    if request.method == 'POST':
        res = dict(success=False, error="", name="", url="")
        
        if request.FILES == None:
            return HttpResponseBadRequest('Must have files attached!')

        #getting file data for farther manipulations
        file = request.FILES[u'files[]']
        wrapped_file = UploadedFile(file)
        filename = wrapped_file.name
        file_size = wrapped_file.file.size
        log.info('Got file: "' + str(filename) + '"')

        try:
           image = Image.open(file)
           #To get the image size, in pixels.    
           (width,height) = image.size
           if width != 256 and height != 256:
              res["success"] = False
              res["error"] = "Image size must be 256x256 px"
           else:            
              log.info('image w:{0} h:{1}'.format(width,height))

              storedimg = StoredImage()
              storedimg.title = ""
              storedimg.image = file
              storedimg.save()

              #getting file url here
              file_url = settings.MEDIA_URL

              res["success"] = True
              res["name"] = str(storedimg)
              res["url"] = file_url
              res["error"] = ""
        except IOError:
           res["success"] = False
           res["error"] = "Format not recognized"

        response_data = json.dumps(res)
        return HttpResponse(response_data, content_type='application/json')
    else:  #GET
        return render_to_response('multiuploader_main.html',
                                  dict(static_url=settings.MEDIA_URL, open_tv=u'{{', close_tv=u'}}'),
        )


def image_view(request):
    items = StoredImage.objects.all()
    return render_to_response('images.html', {'items': items})