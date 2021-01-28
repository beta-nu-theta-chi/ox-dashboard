from urllib.parse import unquote
from django import template

register = template.Library()


@register.filter
def append_ast_if_req(field):
    """ Adds a new filter to template tags that for use in templates. Used by writing {{ field | append_ast_if_req }}
        @register registers the filter into the django template library so it can be used in template.

    :param Form.field field:
        a field of a form that you would like to return the label and potentially an asterisk for.
    :returns:
        The field label and, if it's a required field, an asterisk
    :rtype: string

    """
    if field.field.required:
        return field.label + '*'
    else:
        return field.label