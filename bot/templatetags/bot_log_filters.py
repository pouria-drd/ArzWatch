from django import template

register = template.Library()


@register.filter
def split_lines(value):
    return value.splitlines()
