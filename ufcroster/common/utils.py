import os
from urllib.parse import urlparse

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string


def get_json(url, timeout=2):
    try:
        response = requests.get(url, timeout=timeout)
    except requests.exceptions.Timeout:
        pass
    else:
        if response.status_code == 200:
            return response.json()
    return {}


def restructure_fields_by_template(object_with_fields, template_dictionary):

    existing = set(object_with_fields.fields.keys())
    allowed = set(template_dictionary.keys())

    for key in existing:
        if key in allowed:
            value = template_dictionary[key]
            if isinstance(value, dict):
                restructure_fields_by_template(object_with_fields.fields[key], value)
        else:
            object_with_fields.fields.pop(key)


def get_image_data(url):
    ext = os.path.splitext(urlparse(url)[2])[-1]
    response = requests.get(url)
    return ext, ContentFile(response.content)


def get_ip_from_meta(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def get_data_from_freegeoip(ip):
    """
    Returns:
        {} - in case of timeout or status not 200 or
        e.g. for github.com host:
            {
                "ip":"192.30.253.113",
                "country_code":"US",
                "country_name":"United States",
                "region_code":"CA",
                "region_name":"California",
                "city":"San Francisco",
                "zip_code":"94107",
                "time_zone":"America/Los_Angeles",
                "latitude":37.7697,
                "longitude":-122.3933,
                "metro_code":807
            }
    """
    url = f'https://freegeoip.net/json/{ip}'
    return get_json(url)


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

    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            pass
    return {}
