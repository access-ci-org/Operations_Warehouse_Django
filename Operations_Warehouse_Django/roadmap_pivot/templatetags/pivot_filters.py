# roadmap_pivot/templatetags/pivot_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item by key"""
    return dictionary.get(key, [])


@register.filter
def badge_count_for_status(resource_data, status):
    """Get count of badges for given status"""
    return len(resource_data.get(status, []))
