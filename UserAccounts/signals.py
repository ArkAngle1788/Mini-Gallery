from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile

# from allauth.socialaccount.signals import social_account_added


# remember we have to enable this functionality in apps.py


@receiver(post_save, sender=get_user_model())
def create_profile(sender, instance, created, **kwargs):
    """makes a UserProfile when a User is created"""
    if created:
        UserProfile.objects.create(user=instance)
