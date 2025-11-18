# roadmap_pivot/templatetags/pivot_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item from dictionary by key"""
    if dictionary and key:
        return dictionary.get(str(key))
    return None

@register.filter
def is_verified(status):
    """Check if badge status is verified/completed"""
    if not status:
        return False
    completed_statuses = {'verified', 'tasks-completed', 'complete', 'completed'}
    return status.lower().strip() in completed_statuses

@register.filter
def badge_status_symbol(status):
    """Convert badge status to symbol"""
    if not status:
        return '-'

    status_lower = status.lower().strip()

    if status_lower in {'verified', 'tasks-completed', 'complete', 'completed'}:
        return '<span class="text-success fs-5">&#x2714;</span>'
    elif status_lower in {'not planned', 'not-planned'}:
        return '-'
    else:
        return '<span class="fs-5" style="color: gray;">&#x26A0;</span>'

@register.filter
def trim_access_prefix(name):
    """Remove 'ACCESS ' prefix from badge names"""
    if name and name.startswith('ACCESS '):
        return name[7:]
    return name
