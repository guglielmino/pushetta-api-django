# coding=utf-8

# Progetto: Pushetta Core
# Varie funzioni di utilità usate nel progetto


import logging

logger = logging.getLogger(__name__)

import os
import re
import hashlib

from urlparse import urlparse, urljoin

from PIL import Image
from ghost import Ghost

from django.conf import settings


def check_for_url(text):
    """
    Check if text contains one o more urls
    :param text: text where to look for the urls
    :return: array of found urls
    """

    #p = re.compile(ur'(?:https?:\/\/)?([\da-z\.-]+\.[a-z\.]{2,6}[\/\w]?)')
    p = re.compile(ur'(?:https?:\/\/)?([\da-z\.-]+\.[a-z\.]{2,6}[\/\w]?[]\w\/\.\-]*)')
    return re.findall(p, text)

def grab_url_screenshot(url):
    """
    Grab an url making a screenshot of it
    Filename is SHA256 of url
    :param url:
    :return:
    """

    ret = None

    try:
        # Bonifica url (se manca lo schema assumo http://)
        url_res = urlparse(url)
        if not url_res.scheme:
            url = "http://" + url

        # TODO: Può essere un singleton Ghost?
        ghost = Ghost()
        page, res = ghost.open(url)
        if not page is None and page.http_status == 200:
            url_sha256 = hashlib.sha256(url).hexdigest()
            image_path = os.path.join('url_previews', url_sha256 + ".png")
            full_path = os.path.join(settings.MEDIA_ROOT, image_path)

            ghost.capture_to(full_path)

            image_path = image_path.replace(".png", ".thumb.png")
            thumb_full_path = os.path.join(settings.MEDIA_ROOT,image_path)
            resize_and_crop(full_path, thumb_full_path, (550, 500))
            ret = urljoin(settings.BASE_URL,  "uploads/" + image_path)
        else:
            logger.error("Failed to capture screenshot for {0}".format(url))
    except Exception, e:
        logger.exception(e)
    finally:
        del ghost
    return ret


def resize_and_crop(img_path, modified_path, size, crop_type='top'):
    """
    Resize and crop an image to fit the specified size.

    args:
    img_path: path for the image to resize.
    modified_path: path to store the modified image.
    size: `(width, height)` tuple.
    crop_type: can be 'top', 'middle' or 'bottom', depending on this
    value, the image will cropped getting the 'top/left', 'middle' or
    'bottom/right' of the image to fit the size.
    raises:
    Exception: if can not open the file in img_path of there is problems
    to save the image.
    ValueError: if an invalid `crop_type` is provided.
    """
    # If height is higher we resize vertically, if not we resize horizontally
    img = Image.open(img_path)
    # Get current and desired ratio for the images
    img_ratio = img.size[0] / float(img.size[1])
    ratio = size[0] / float(size[1])
    #The image is scaled/cropped vertically or horizontally depending on the ratio
    if ratio > img_ratio:
        img = img.resize((size[0], int(round(size[0] * img.size[1] / img.size[0]))),
            Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, img.size[0], size[1])
        elif crop_type == 'middle':
            box = (0, int(round((img.size[1] - size[1]) / 2)), img.size[0],
                int(round((img.size[1] + size[1]) / 2)))
        elif crop_type == 'bottom':
            box = (0, img.size[1] - size[1], img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    elif ratio < img_ratio:
        img = img.resize((int(round(size[1] * img.size[0] / img.size[1])), size[1]),
            Image.ANTIALIAS)
        # Crop in the top, middle or bottom
        if crop_type == 'top':
            box = (0, 0, size[0], img.size[1])
        elif crop_type == 'middle':
            box = (int(round((img.size[0] - size[0]) / 2)), 0,
                int(round((img.size[0] + size[0]) / 2)), img.size[1])
        elif crop_type == 'bottom':
            box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
        else :
            raise ValueError('ERROR: invalid value for crop_type')
        img = img.crop(box)
    else :
        img = img.resize((size[0], size[1]),
            Image.ANTIALIAS)
    # If the scale is the same, we do not need to crop
    img.save(modified_path)