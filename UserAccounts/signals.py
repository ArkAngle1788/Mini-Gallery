from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver

# from allauth.socialaccount.signals import social_account_added

from .models import UserProfile

# remember we have to enable this functionality in apps.py


# @receiver(social_account_added)
# def create_profile(request,sociallogin,**kwargs):#this signal is received when i social account is linked. You can link a social account to an existing account so we need to check if a profile already exists
#
#     try :
#         request.user.profile
#         #if this works it means that profile already exists so we do not need to do anything here
#         print("no error")
#     except:
#         print("error")
#         new_userprofile=UserProfile(user=request.user)
#         new_userprofile.save()


@receiver(post_save,sender=User)
def create_profile(sender, instance,created,**kwargs):
    if created:
        UserProfile.objects.create(user=instance)


# post_save.connect(create_colour_catagory, sender=Colour)
