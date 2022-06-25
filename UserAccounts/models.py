from django.db import models
from django.contrib.auth.models import User
from League.models import Player,League
from CommunityInfrastructure.models import Group,City
from django.urls import reverse


# if request.user.groups.filter(name="group_name").exists():



# Next task: set up account creation so that both name and user name are required fields


class UserProfile(models.Model):



    # a User is like a web account and a UserProfile is our custom data  -- a user and userprofile will always be linked
    user = models.OneToOneField(User,on_delete=models.CASCADE, related_name='profile') #we call profile instead of userprofile b/c we always reverse look up from the django user account
    # User has a username and firstname/lastname fields
    #  it is best practice to call username using .get_username() from templates since User can be replaced

    location=models.ForeignKey(City,on_delete=models.SET_NULL,blank=True,null=True,related_name='users_in_city')

    approved_by=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True,related_name='approved_users')

    #  this is a redundant step of data storage. There should be no reason a league profile can't be merged with a user profile (psf can be used to identify activity)
        # an account might not have participated in a league and thus will have this entry null   -reverse lookup is web_profile because we would access it from the specific league information of a player
        # league_profile=models.OneToOneField(Player,on_delete=models.SET_NULL, related_name='web_profile',null=True,blank=True)

# this is now split between AdminProfile and permissions -- AdminProfile to track which league you're actually in charge of and permissions for global admin privilages (like gallery)
    # league_admin=models.BooleanField(default=False)
    # permission_level=models.IntegerField(null=True,default=basic_user_permission) #have 0 be root and set a basic user to like 20? or maybe null?  use this to check if a user can do things like create a league


# trused status is also probably better handled in a role asking to be trused is probably not a scalable system and needs a full rework
    # basic functionality no longer needs trusted status. maybe use this for images and community content submission
    # please_trust_me=models.BooleanField(default=False) #have an admin page that shows all users asking to be trusted and have a button to give them trust privilage
    # trusted=models.BooleanField(default=False) #can access a page to configure league profile settings (faction,display name, ect.)


# Trusted Satus, what if we set a field that tracks an admin and that field counts as being trusted. That way it's a referal based system and if there are problems with a user we can see who added them.
# we could then later on add a special case for web only authentication if that's a direction we want to develop in

    # when checking from the html a user might not have a Admin profile so we need to check using UserProfile

    def is_primary_admin(group):
        for admin in group.group_primary_admins.all():
            if admin.userprofile == self.userprofile:
                return True
        return False

    def is_secondary_admin(group):
        for admin in group.group_secondary_admins.all():
            if admin.userprofile == self.userprofile:
                return True
        return False

    def get_absolute_url(self):
        return reverse('profile self')

    def __str__(self):
        return self.user.username



# maybe have a role that you must have in order to interact with this class
# that way you you lose admin permissions all this stay the same and it's as simple as adding/removing the roles to manage

# why is this here instead of a property of a group? Because a group does not know about other groups so this way you only lose/gain privilages when a list empties or is populated

class AdminProfile(models.Model):
    class Meta:
        permissions = [
            ("approve_users", "Can enable a user to upload images"),
        ]

    userprofile = models.OneToOneField(UserProfile,on_delete=models.CASCADE, related_name='linked_admin_profile')

    # you might be involved in managment for multiple groups so permissions need to be defined on a group by group level
    groups_managed_primary=models.ManyToManyField(Group,blank=True,related_name='group_primary_admins')
    groups_managed_secondary=models.ManyToManyField(Group,blank=True,related_name='group_secondary_admins')

    #above a certain permission/role threshold you can manage leagues not explicitly given to you
    leagues_managed=models.ManyToManyField(League,blank=True,related_name='admins_manageing')   #this will be a list of all the leagues a user has permission to manage.

    def is_primary_admin(group):
        for admin in group.group_primary_admins.all():
            if admin.userprofile == self.userprofile:
                return True
        return False

    def is_secondary_admin(group):
        for admin in group.group_secondary_admins.all():
            if admin.userprofile == self.userprofile:
                return True
        return False

    def __str__(self):
        return self.userprofile.__str__()
