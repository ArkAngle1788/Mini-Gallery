# from django.db.models.signals import post_save
from django.dispatch import receiver

from CommunityInfrastructure.custom_functions import new_studio_image

# from .models import StudioImages



# remember we have to enable this functionality in apps.py


@receiver(signal=new_studio_image)
def update_studio_images(sender, image, studio, **kwargs):
    """
    listens for new_studio_image signal
    sender is currently unused
    """
    #_set lets us reverse lookup the relationship
    throughobject=image.studioimages_set.get(studio_id=studio.pk)
    throughobject.official=True
    throughobject.save()
