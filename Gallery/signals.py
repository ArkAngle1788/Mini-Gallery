from django.db.models.signals import post_save,m2m_changed
from django.dispatch import receiver

from .models import Colour_Catagory,Colour,Colour_Priority,UserImage


# remember we have to enable this functionality in apps.py

@receiver(post_save,sender=Colour)
def create_colour_catagory_from_colour(sender, instance, created, **kwargs):
    if created:
        for priority in Colour_Priority.objects.all():
            Colour_Catagory.objects.create(colour=instance,colour_priority=priority)

@receiver(post_save,sender=Colour_Priority)
def create_colour_catagory_from_priority(sender, instance, created, **kwargs):
    if created:
        for colour in Colour.objects.all():
            Colour_Catagory.objects.create(colour=colour,colour_priority=instance)


# all of the below is a huge yikes. It will need to be revisited for efficiency once i understand signals better

@receiver(m2m_changed,sender=UserImage.system.through)
def update_fuzzy_search_tag(sender, instance,  **kwargs):
    fuzzy_tag=''
    for var in instance.system.all():
        fuzzy_tag+=var.__str__()
    for var in instance.faction_type.all():
        fuzzy_tag+=var.__str__()
    for var in instance.factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.sub_factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.colours.all():
        fuzzy_tag+=var.__str__()
    for var in instance.unit_type.all():
        fuzzy_tag+=var.__str__()
    fuzzy_tag+=instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)

@receiver(m2m_changed,sender=UserImage.faction_type.through)
def update_fuzzy_search_tag2(sender, instance,  **kwargs):
    fuzzy_tag=''
    for var in instance.system.all():
        fuzzy_tag+=var.__str__()
    for var in instance.faction_type.all():
        fuzzy_tag+=var.__str__()
    for var in instance.factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.sub_factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.colours.all():
        fuzzy_tag+=var.__str__()
    for var in instance.unit_type.all():
        fuzzy_tag+=var.__str__()
    fuzzy_tag+=instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)

@receiver(m2m_changed,sender=UserImage.factions.through)
def update_fuzzy_search_tag3(sender, instance,  **kwargs):
    fuzzy_tag=''
    for var in instance.system.all():
        fuzzy_tag+=var.__str__()
    for var in instance.faction_type.all():
        fuzzy_tag+=var.__str__()
    for var in instance.factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.sub_factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.colours.all():
        fuzzy_tag+=var.__str__()
    for var in instance.unit_type.all():
        fuzzy_tag+=var.__str__()
    fuzzy_tag+=instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)

@receiver(m2m_changed,sender=UserImage.sub_factions.through)
def update_fuzzy_search_tag4(sender, instance,  **kwargs):
    fuzzy_tag=''
    for var in instance.system.all():
        fuzzy_tag+=var.__str__()
    for var in instance.faction_type.all():
        fuzzy_tag+=var.__str__()
    for var in instance.factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.sub_factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.colours.all():
        fuzzy_tag+=var.__str__()
    for var in instance.unit_type.all():
        fuzzy_tag+=var.__str__()
    fuzzy_tag+=instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)

@receiver(m2m_changed,sender=UserImage.colours.through)
def update_fuzzy_search_tag5(sender, instance,  **kwargs):
    fuzzy_tag=''
    for var in instance.system.all():
        fuzzy_tag+=var.__str__()
    for var in instance.faction_type.all():
        fuzzy_tag+=var.__str__()
    for var in instance.factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.sub_factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.colours.all():
        fuzzy_tag+=var.__str__()
    for var in instance.unit_type.all():
        fuzzy_tag+=var.__str__()
    fuzzy_tag+=instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)

@receiver(m2m_changed,sender=UserImage.unit_type.through)
def update_fuzzy_search_tag6(sender, instance,  **kwargs):
    fuzzy_tag=''
    for var in instance.system.all():
        fuzzy_tag+=var.__str__()
    for var in instance.faction_type.all():
        fuzzy_tag+=var.__str__()
    for var in instance.factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.sub_factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.colours.all():
        fuzzy_tag+=var.__str__()
    for var in instance.unit_type.all():
        fuzzy_tag+=var.__str__()
    fuzzy_tag+=instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)

@receiver(post_save,sender=UserImage)
def update_fuzzy_search_tag7(sender, instance,  **kwargs):
    fuzzy_tag=''
    for var in instance.system.all():
        fuzzy_tag+=var.__str__()
    for var in instance.faction_type.all():
        fuzzy_tag+=var.__str__()
    for var in instance.factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.sub_factions.all():
        fuzzy_tag+=var.__str__()
    for var in instance.colours.all():
        fuzzy_tag+=var.__str__()
    for var in instance.unit_type.all():
        fuzzy_tag+=var.__str__()
    fuzzy_tag+=instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)
