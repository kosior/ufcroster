from django import template

register = template.Library()


result_to_bagde = {
    'W': 'success',
    'L': 'danger',
    'D': 'info',
    'NC': 'light'
}


@register.simple_tag
def result_badge(result):
    return result_to_bagde.get(result)
