# -*- coding: utf-8 -*-
from __future__ import absolute_import

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app
from core import signal

__version__ = '1.1.3'
__build__ = ''
