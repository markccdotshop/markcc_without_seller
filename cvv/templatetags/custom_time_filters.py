from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def hours_since(value, default="just now"):
    if not value:
        return default

    # Get the most significant unit only
    time_str = timesince(value).split(', ')[0]
    
    # Define allowed time units and include their plural forms and weeks
    allowed_units = [
        "minute", "minutes",
        "hour", "hours",
        "day", "days",
        "week", "weeks",  # Added weeks
        "month", "months",
        "year", "years"
    ]
    
    # Check if any allowed units are in the string
    if any(unit in time_str for unit in allowed_units):
        return time_str
    else:
        return default
