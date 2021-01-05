from urllib.parse import unquote
from django import template

register = template.Library()

@register.filter
def append_ast_if_req(field):
    if field.field.required:
        return field.label + '*'
    else:
        return field.label