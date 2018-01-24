import os
from urllib.parse import urlparse

import requests
from django.core.files.base import ContentFile


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
