from django import template
from urllib.parse import urlencode


register = template.Library()

@register.simple_tag
def url_replace (request, field, value):
    dict_ = request.GET.copy()
    dict_[field] = value

    return dict_.urlencode()

@register.filter
def replace_commas(string):
    return string.replace(':', '|')




@register.filter(name='star_rating')
def star_rating(rating):
    full_stars = int(rating)  # Convert to integer to get full stars
    empty_stars = 5 - full_stars  # Assuming 5 as the max rating
    return '★' * full_stars + '☆' * empty_stars  # Using Unicode characters