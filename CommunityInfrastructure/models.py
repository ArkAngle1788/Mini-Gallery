from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


class Country(models.Model):
    """
    params: country_name
    get_absolute_url returns groups top
    """
    country_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.country_name)

    def get_absolute_url(self):
        """returns groups top"""
        return reverse('groups top')


class Region(models.Model):
    """get_absolute_url returns groups top"""
    region_name = models.CharField(max_length=50, unique=True)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, blank=False, null=False, related_name='country_regions')

    def __str__(self):
        return str(self.region_name)

    def get_absolute_url(self):
        """returns groups top"""
        return reverse('groups top')


class City(models.Model):
    """get_absolute_url returns groups top"""
    city_name = models.CharField(max_length=50, unique=True)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, blank=False, null=False, related_name='region_cities')

    def __str__(self):
        return str(self.city_name)

    def get_absolute_url(self):
        """returns groups top"""
        return reverse('groups top')


class PaintingStudio(models.Model):
    """
    Painting Studio has a single User that manages it
    """
    Studio_name = models.CharField(max_length=50)
    Studio_page = models.CharField(max_length=100)
    description = models.CharField(max_length=1000)
    location = models.ForeignKey(
        City, on_delete=models.SET_NULL, blank=False, null=True, related_name='studios_in_city')
    userprofile = models.ForeignKey(
        get_user_model(), on_delete=models.SET_NULL, blank=True, null=True,
        related_name='studios_managed')

    def __str__(self):
        return str(self.Studio_name)

    def get_absolute_url(self):
        """returns groups top"""
        return reverse('groups top')

    def slug(self):
        """slugifys on studio_name"""
        return slugify(self.Studio_name)


class StudioImages(models.Model):
    """
    tracks images that have been uploaded
    through the studio page interface.
    """
    studio = models.ForeignKey(PaintingStudio, on_delete=models.CASCADE)
    image = models.ForeignKey('Gallery.UserImage', on_delete=models.CASCADE)
    official = models.BooleanField(default=False)


class Language(models.Model):
    """Not implemented yet"""
    language = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return str(self.language)


def validate_int_list(value):
    """
    splits a list on ',' and checks that each item is an int
    """

    img_list = value.split(',')

    for item in img_list:
        try:
            int(item)
        except ValueError:
            raise ValidationError('Invalid Format')


class Group(models.Model):
    """
    Can only have one of
    location_city location_region location_country set
    """

    group_name = models.CharField(max_length=50, unique=True)
    # slug = models.SlugField(max_length=50)
    group_tag = models.CharField(max_length=50)
    group_description = models.CharField(max_length=600)
    group_image_str = models.CharField(
        max_length=50, null=True,blank=True, validators=[validate_int_list])
    group_leagues = models.ManyToManyField(
        'League.League', blank=True, related_name='group_running')

    # will need to have carefull app logic to ensure
    # only one of these gets set since that's how we will check for scope
    location_city = models.ForeignKey(
        City, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='groups_in_city')
    location_region = models.ForeignKey(
        Region, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='groups_in_region')
    location_country = models.ForeignKey(
        Country, on_delete=models.SET_NULL, blank=True, null=True,
        related_name='groups_in_country')

    def slug(self):
        """slugify on group_name"""
        return slugify(self.group_name)

    def get_absolute_url(self):
        """
        calculates group info arg based off of
        if group has city region or country set
        """

        if self.location_city:
            loc = str(self.location_city)
        elif self.location_region:
            loc = str(self.location_region)
        elif self.location_country:
            loc = str(self.location_country)
        else:
            return reverse('home')

        return reverse('group info', kwargs={'zone': loc, 'group_slug': self.slug(), 'pk': self.pk})

    def __str__(self):
        return str(self.group_name)
