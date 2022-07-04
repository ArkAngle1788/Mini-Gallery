from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.contrib.auth.models import User
# from Gallery.models import UserImage


class Country(models.Model):
    country_name=models.CharField(max_length=50,unique=True)
    def __str__(self):
        return self.country_name
    def get_absolute_url(self):
        return reverse('groups top')

class Region(models.Model):
    region_name=models.CharField(max_length=50,unique=True)
    country=models.ForeignKey(Country,on_delete=models.CASCADE,blank=False,null=False,related_name='country_regions')
    def __str__(self):
        return self.region_name
    def get_absolute_url(self):
        return reverse('groups top')

class City(models.Model):
    city_name=models.CharField(max_length=50,unique=True)
    region=models.ForeignKey(Region,on_delete=models.CASCADE,blank=False,null=False,related_name='region_cities')
    def __str__(self):
        return self.city_name
    def get_absolute_url(self):
        return reverse('groups top')


class PaintingStudio(models.Model):
    Studio_name=models.CharField(max_length=50)
    Studio_page=models.CharField(max_length=100) #are these fields security vunerablilites?
    description=models.CharField(max_length=1000)
    location=models.ForeignKey(City,on_delete=models.SET_NULL,blank=False,null=True,related_name='studios_in_city')
    userprofile=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True,related_name='studios_managed')
    # studio_images=models.ManyToManyField(UserImage,blank=True,related_name='belonging_studio')
    def __str__(self):
        return self.Studio_name
    def get_absolute_url(self):
        return reverse('groups top')
    def slug(self):
        return slugify(self.Studio_name)

class Studio_Images(models.Model):
    studio = models.ForeignKey(PaintingStudio, on_delete=models.CASCADE)
    image = models.ForeignKey('Gallery.UserImage', on_delete=models.CASCADE)
    official = models.BooleanField(default=False)

class Language(models.Model):
    language=models.CharField(max_length=20,unique=True)
    def __str__(self):
        return self.language

# from League.models import LeagueModel

class Group(models.Model):

    group_name=models.CharField(max_length=50,unique=True)
    slug = models.SlugField(max_length=50)
    group_tag=models.CharField(max_length=50)
    group_description=models.CharField(max_length=600)

    group_leagues=models.ManyToManyField('League.League',blank=True,related_name='group_running')#this many to many is a string to help solve circlular imports i think?


    # this has been moved to a user AdminProfile property
    # group_admins=models.ManyToManyField(AdminProfile,blank=True,null=True,related_name='groups_managed')

    # will need to have carefull app logic to ensure only one of these gets set since that's how we will check for scope
    location_city=models.ForeignKey(City,on_delete=models.SET_NULL,blank=True,null=True,related_name='groups_in_city')
    location_region=models.ForeignKey(Region,on_delete=models.SET_NULL,blank=True,null=True,related_name='groups_in_region')
    location_country=models.ForeignKey(Country,on_delete=models.SET_NULL,blank=True,null=True,related_name='groups_in_country')

    def slug(self):
        return slugify(self.group_name)

    def get_absolute_url(self):

        if self.location_city:
            loc=self.location_city.__str__()
        elif self.location_region:
            loc=self.location_region.__str__()
        elif self.location_country:
            loc=self.location_country.__str__()
        else:
            return reverse('home')

        return reverse('group info',kwargs={'zone':loc,'group_slug':self.slug(),'pk':self.pk})
        # return reverse('home')

    def __str__(self):
        return self.group_name
