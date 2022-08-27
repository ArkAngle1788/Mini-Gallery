from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from CommunityInfrastructure.models import City, Group
from League.models import League


class UserProfile(models.Model):
    """
    a User is like a web account and a UserProfile is our custom data
    -- a user and userprofile will always be linked
    """

    # we call profile instead of userprofile b/c
    # we always reverse look up from the django user account
    user = models.OneToOneField(
        get_user_model(), on_delete=models.CASCADE, related_name='profile')
    # User has a username and firstname/lastname fields

    location = models.ForeignKey(
        City, on_delete=models.SET_NULL, blank=True, null=True, related_name='users_in_city')
    approved_by = models.ForeignKey(get_user_model(
    ), on_delete=models.SET_NULL, blank=True, null=True, related_name='approved_users')

    # when checking from the html a user might
    # not have a Admin profile so we need to check using UserProfile

    def is_primary_admin(self, group):
        """returns true if the UserProfile is present in group.group_primary_admins"""
        for admin in group.group_primary_admins.all():
            if admin.userprofile == self:
                return True
        return False

    def is_secondary_admin(self, group):
        """returns true if the UserProfile is present in group.group_secondary_admins"""
        for admin in group.group_secondary_admins.all():
            if admin.userprofile == self:
                return True
        return False

    def get_absolute_url(self):
        """returns 'profile self'"""
        return reverse('profile self')

    def __str__(self):
        return str(self.user)


# maybe have a role that you must have in order to interact with this class
# that way you you lose admin permissions all this stay the same
# and it's as simple as adding/removing the roles to manage

# why is this here instead of a property of a group?
# Because a group does not know about other groups so this way
# you only lose/gain privilages when a list empties or is populated

class AdminProfile(models.Model):
    """
    This model stores group admin status for a UserProfile
    because a single user might admin multipule groups
    """
    class Meta:
        permissions = [
            # creates a new permission to be used by admins
            ("approve_users", "Can enable a user to upload images"),
        ]

    userprofile = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name='linked_admin_profile')

    # you might be involved in managment for multiple groups
    # so permissions need to be defined on a group by group level
    groups_managed_primary = models.ManyToManyField(
        Group, blank=True, related_name='group_primary_admins')
    groups_managed_secondary = models.ManyToManyField(
        Group, blank=True, related_name='group_secondary_admins')

    # above a certain permission/role threshold you can manage leagues not explicitly given to you

    # this will be a list of all the leagues a user has permission to manage.
    leagues_managed = models.ManyToManyField(
        League, blank=True, related_name='admins_manageing')

    def is_primary_admin(self, group):
        """returns true if the UserProfile is present in group.group_primary_admins"""
        for admin in group.group_primary_admins.all():
            if admin.userprofile == self.userprofile:
                return True
        return False

    def is_secondary_admin(self, group):
        """returns true if the UserProfile is present in group.group_secondary_admins"""
        for admin in group.group_secondary_admins.all():
            if admin.userprofile == self.userprofile:
                return True
        return False

    def __str__(self):
        return self.userprofile.__str__()
