from django import template

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

