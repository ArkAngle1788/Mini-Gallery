from django import template
from CommunityInfrastructure.models import Group
# from .models import

register = template.Library()



@register.filter
def is_primary_admin(group,user):
    for admin in group.group_primary_admins.all():
        if admin.userprofile == user.profile:
            return True
    return False

@register.filter
def is_secondary_admin(group,user):
    for admin in group.group_secondary_admins.all():
        if admin.userprofile == user.profile:
            return True
    return False

@register.filter
def simple_test(var):

    return "var"
