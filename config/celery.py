from __future__ import absolute_import, unicode_literals

import os
import sys

import django
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

sys.path.append(os.path.join(str(settings.ROOT_DIR), 'ufcroster'))
django.setup()

app = Celery('ufcroster')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
