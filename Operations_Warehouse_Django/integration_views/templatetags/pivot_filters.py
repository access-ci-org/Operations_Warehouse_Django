# roadmap_pivot/templatetags/pivot_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get item by key"""
    return dictionary.get(key, [])


@register.filter
def badge_status_symbol(status):
    """Convert badge status to legend symbol"""
    if status == 'verified':
        return '<span class="text-success fs-4">&#x2714;</span>'  # Green check - In Production
    elif status == 'planned':
        return '<span class="fs-4" style="color: gray;">&#x26A0;</span>'  # In-Progress
    else:
        return '-'  # Dash - Not Planned (None, retired, verification_failed, etc.) - Neither in-Progress or in production

# trimming out 'ACCESS ' from the bage name if present
@register.filter
def trim_access_prefix(badge_name):
    """Remove 'ACCESS ' prefix from badge name if present"""
    if badge_name and badge_name.startswith('ACCESS '):
        return badge_name[7:] 
    return badge_name