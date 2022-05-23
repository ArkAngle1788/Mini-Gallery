from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Studio_Images

from .views import new_studio_image


# remember we have to enable this functionality in apps.py


@receiver(signal=new_studio_image)
def update_studio_images(sender, image, studio, **kwargs):
    # print('\nsignal received\n'+str(image))
    # print("studio is : ")
    # print(studio.pk)
    # print(f"studio_images.all is : {image.studio_images_set}\n")
    throughobject=image.studio_images_set.get(studio_id=studio.pk)#_set lets us reverse lookup the relationship
    # print(f"throughobject is : {throughobject}\n")
    # print(f' official is : {throughobject.official}')
    throughobject.official=True
    throughobject.save()
    # print(throughobject.official)




# post_save.connect(create_colour_catagory, sender=Colour)
