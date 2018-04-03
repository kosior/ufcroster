from django import template
from django.conf import settings
from django_countries.fields import Country


register = template.Library()


@register.simple_tag
def get_country(code):
    return Country(code=code)


@register.simple_tag
def get_active_countries():
    return [get_country(country_code) for country_code in settings.COUNTRIES_URL_CODES]
