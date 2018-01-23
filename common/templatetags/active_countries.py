from django import template
from django.conf import settings
from django_countries.fields import Country


register = template.Library()


@register.simple_tag
def get_country(code):
    return Country(code=code)


@register.simple_tag
def get_active_countries():
    return list(get_country(country.upper()) for country in settings.COUNTRIES_URL_CODES)
