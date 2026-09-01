import json
from django import template

register = template.Library()

@register.filter(name='pretty_json')
def pretty_json(value):
    try:
        # If it's already a dict/list (e.g. from JSONField), dump it
        if isinstance(value, (dict, list)):
            return json.dumps(value, indent=4)
        # If it's a string, load it first to validate, then dump it pretty
        return json.dumps(json.loads(value), indent=4)
    except (ValueError, TypeError):
        return value
