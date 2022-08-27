from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver

from .models import Colour, ColourCatagory, ColourPriority, UserImage

# remember we have to enable this functionality in apps.py


@receiver(post_save, sender=Colour)
def create_colour_catagory_from_colour(sender, instance, created, **kwargs):
    """when colour is saved make a new ColourPriority using the value"""
    if created:
        for priority in ColourPriority.objects.all():
            ColourCatagory.objects.create(
                colour=instance, colourpriority=priority)


@receiver(post_save, sender=ColourPriority)
def create_colour_catagory_from_priority(sender, instance, created, **kwargs):
    """when a Priority is saved make a new ColourPriority using the value"""
    if created:
        for colour in Colour.objects.all():
            ColourCatagory.objects.create(
                colour=colour, colourpriority=instance)


# all of the below is a huge yikes.
# It will need to be revisited for efficiency once i understand signals better

@receiver(m2m_changed, sender=UserImage.system.through)
def update_fuzzy_search_tag(sender, instance,  **kwargs):
    """signals on UserImage m2m system changing"""
    fuzzy_tag = ''
    for var in instance.system.all():
        fuzzy_tag += str(var)
    for var in instance.faction_type.all():
        fuzzy_tag += str(var)
    for var in instance.factions.all():
        fuzzy_tag += str(var)
    for var in instance.sub_factions.all():
        fuzzy_tag += str(var)
    for var in instance.colours.all():
        fuzzy_tag += str(var)
    for var in instance.unit_type.all():
        fuzzy_tag += str(var)
    fuzzy_tag += instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)


@receiver(m2m_changed, sender=UserImage.faction_type.through)
def update_fuzzy_search_tag2(sender, instance,  **kwargs):
    """signals on UserImage m2m faction_type changing"""
    fuzzy_tag = ''
    for var in instance.system.all():
        fuzzy_tag += str(var)
    for var in instance.faction_type.all():
        fuzzy_tag += str(var)
    for var in instance.factions.all():
        fuzzy_tag += str(var)
    for var in instance.sub_factions.all():
        fuzzy_tag += str(var)
    for var in instance.colours.all():
        fuzzy_tag += str(var)
    for var in instance.unit_type.all():
        fuzzy_tag += str(var)
    fuzzy_tag += instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)


@receiver(m2m_changed, sender=UserImage.factions.through)
def update_fuzzy_search_tag3(sender, instance,  **kwargs):
    """signals on UserImage m2m factions changing"""
    fuzzy_tag = ''
    for var in instance.system.all():
        fuzzy_tag += str(var)
    for var in instance.faction_type.all():
        fuzzy_tag += str(var)
    for var in instance.factions.all():
        fuzzy_tag += str(var)
    for var in instance.sub_factions.all():
        fuzzy_tag += str(var)
    for var in instance.colours.all():
        fuzzy_tag += str(var)
    for var in instance.unit_type.all():
        fuzzy_tag += str(var)
    fuzzy_tag += instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)


@receiver(m2m_changed, sender=UserImage.sub_factions.through)
def update_fuzzy_search_tag4(sender, instance,  **kwargs):
    """signals on UserImage m2m sub_factions changing"""
    fuzzy_tag = ''
    for var in instance.system.all():
        fuzzy_tag += str(var)
    for var in instance.faction_type.all():
        fuzzy_tag += str(var)
    for var in instance.factions.all():
        fuzzy_tag += str(var)
    for var in instance.sub_factions.all():
        fuzzy_tag += str(var)
    for var in instance.colours.all():
        fuzzy_tag += str(var)
    for var in instance.unit_type.all():
        fuzzy_tag += str(var)
    fuzzy_tag += instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)


@receiver(m2m_changed, sender=UserImage.colours.through)
def update_fuzzy_search_tag5(sender, instance,  **kwargs):
    """signals on UserImage m2m colours changing"""
    fuzzy_tag = ''
    for var in instance.system.all():
        fuzzy_tag += str(var)
    for var in instance.faction_type.all():
        fuzzy_tag += str(var)
    for var in instance.factions.all():
        fuzzy_tag += str(var)
    for var in instance.sub_factions.all():
        fuzzy_tag += str(var)
    for var in instance.colours.all():
        fuzzy_tag += str(var)
    for var in instance.unit_type.all():
        fuzzy_tag += str(var)
    fuzzy_tag += instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)


@receiver(m2m_changed, sender=UserImage.unit_type.through)
def update_fuzzy_search_tag6(sender, instance,  **kwargs):
    """signals on UserImage m2m unit_type changing"""
    fuzzy_tag = ''
    for var in instance.system.all():
        fuzzy_tag += str(var)
    for var in instance.faction_type.all():
        fuzzy_tag += str(var)
    for var in instance.factions.all():
        fuzzy_tag += str(var)
    for var in instance.sub_factions.all():
        fuzzy_tag += str(var)
    for var in instance.colours.all():
        fuzzy_tag += str(var)
    for var in instance.unit_type.all():
        fuzzy_tag += str(var)
    fuzzy_tag += instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)


@receiver(post_save, sender=UserImage)
def update_fuzzy_search_tag7(sender, instance,  **kwargs):
    """signals on UserImage non-m2m fields saving"""
    fuzzy_tag = ''
    for var in instance.system.all():
        fuzzy_tag += str(var)
    for var in instance.faction_type.all():
        fuzzy_tag += str(var)
    for var in instance.factions.all():
        fuzzy_tag += str(var)
    for var in instance.sub_factions.all():
        fuzzy_tag += str(var)
    for var in instance.colours.all():
        fuzzy_tag += str(var)
    for var in instance.unit_type.all():
        fuzzy_tag += str(var)
    fuzzy_tag += instance.image_title
    UserImage.objects.filter(pk=instance.pk).update(fuzzy_tags=fuzzy_tag)
