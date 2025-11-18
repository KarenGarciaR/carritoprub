from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """Subtract the argument from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, percentage):
    """Calculate percentage of value."""
    try:
        return float(value) * (float(percentage) / 100)
    except (ValueError, TypeError):
        return 0

@register.filter
def timesince_days(value):
    """Get number of days since the given datetime."""
    from django.utils import timezone
    import datetime
    
    if not value:
        return 0
    
    now = timezone.now()
    if isinstance(value, datetime.datetime):
        diff = now - value
        return diff.days
    return 0

@register.filter
def currency(value):
    """Format value as currency."""
    try:
        return "${:.2f}".format(float(value))
    except (ValueError, TypeError):
        return "$0.00"