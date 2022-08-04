from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Studio_Images

from CommunityInfrastructure.custom_functions import new_studio_image


# remember we have to enable this functionality in apps.py


@receiver(signal=new_studio_image)
def update_studio_images(sender, image, studio, **kwargs):
    throughobject=image.studio_images_set.get(studio_id=studio.pk)#_set lets us reverse lookup the relationship
    throughobject.official=True
    throughobject.save()
