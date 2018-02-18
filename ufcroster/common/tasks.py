import requests
from celery.task import task
from django.conf import settings
from django.template.loader import render_to_string


@task
def send_email(to, subject, text='', template_name=None, context=None):
    data = {
        'from': settings.MAIL_FROM_NO_REPLY,
        'to': to,
        'subject': subject,
        'text': text,
    }

    if template_name:
        data['html'] = render_to_string(template_name, context)

    if isinstance(to, list):
        data['recipient-variables'] = '{}'

    response = requests.post(settings.MAILGUN_SEND_URL, auth=('api', settings.MAILGUN_KEY), data=data)
    return response.status_code, response.text
