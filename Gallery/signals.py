from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Colour_Catagory,Colour,Colour_Priority


# remember we have to enable this functionality in apps.py

@receiver(post_save,sender=Colour)
def create_colour_catagory_from_colour(sender, instance, created, **kwargs):
    if created:
        for priority in Colour_Priority.objects.all():
            Colour_Catagory.objects.create(colour=instance,colour_priority=priority)
            print("creating: "+f'/{instance} and {priority}')

@receiver(post_save,sender=Colour_Priority)
def create_colour_catagory_from_priority(sender, instance, created, **kwargs):
    if created:
        for colour in Colour.objects.all():
            Colour_Catagory.objects.create(colour=colour,colour_priority=instance)
            print("creating: "+f'/{instance} and {colour}')





# post_save.connect(create_colour_catagory, sender=Colour)
