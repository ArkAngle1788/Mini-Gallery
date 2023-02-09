from django import template
from League.custom_functions import match_permission_check as league_match_permission_check
# from .models import

register = template.Library()



@register.filter
def match_permission_check(match,user):

    return league_match_permission_check(match,user)
