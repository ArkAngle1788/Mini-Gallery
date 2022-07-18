from django.db import models
from GameData.models import Games, Faction, Faction_Type, Sub_Faction, Unit_Type
from CommunityInfrastructure.models import PaintingStudio,Studio_Images, Country,Region,City
from League.models import Season
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date


class Conversion(models.Model):
    conversion_type = models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.conversion_type




class Scale_Of_Image(models.Model):# amount of content in picutre ex. single model, 2000pt army, entire collection
    scale = models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.scale

class Colour(models.Model):
    colour_name = models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.colour_name
    def get_absolute_url(self):
        return reverse('manage image fields')

class Colour_Priority(models.Model):
    colour_priority = models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.colour_priority
    def get_absolute_url(self):
        return reverse('manage image fields')


class Colour_Catagory(models.Model):#a combination of a colour and a level of prominance
    colour_priority = models.ForeignKey(Colour_Priority,on_delete=models.CASCADE,related_name='colour_priority_group')#this might be something like 'primary or secondary'
    colour=models.ForeignKey(Colour,on_delete=models.CASCADE,related_name='colour_group')

    def __str__(self):
        return f'{self.colour_priority} {self.colour}'
    def get_absolute_url(self):
        return reverse('manage image fields')

def get_upload_to():
    current_year = str(date.today().year)
    current_month = str(date.today().month)
    return 'gallery_images/'+current_year+'/'+current_month

def sub_get_upload_to():
    current_year = str(date.today().year)
    current_month = str(date.today().month)
    return 'gallery_sub_images/'+current_year+'/'+current_month

def temp_get_upload_to():
    current_year = str(date.today().year)
    current_month = str(date.today().month)
    return 'staging_images/'+current_year+'/'+current_month

class TempImage(models.Model):
    image=models.ImageField(upload_to=temp_get_upload_to())
    uploader=models.ForeignKey(User,on_delete=models.CASCADE)
    def __str__(self):
        return str(self.pk)


class UserImage(models.Model):

    image = models.ImageField(upload_to=get_upload_to())
    image_title=models.CharField(max_length=50)

    system=models.ManyToManyField(Games,blank=True)
    faction_type=models.ManyToManyField(Faction_Type,blank=True,related_name='image_faction_types_present')
    factions=models.ManyToManyField(Faction,blank=True,related_name='image_factions_present')
    sub_factions=models.ManyToManyField(Sub_Faction,blank=True,related_name='image_sub_factions_present')
    colours=models.ManyToManyField(Colour_Catagory,blank=True,related_name='Colours_in_image')
    conversion=models.ManyToManyField(Conversion,blank=True,related_name='image_conversions')
    unit_type=models.ManyToManyField(Unit_Type,blank=True,related_name='image_unit_types_present')
    scale=models.ForeignKey(Scale_Of_Image,blank=True,null=True,on_delete=models.SET_NULL,related_name='scale_of_image')
    paintingstudio=models.ManyToManyField(PaintingStudio,blank=True,through='CommunityInfrastructure.Studio_Images',related_name='studios_images')#this relationship is defined here and not present in PaintingStudio because it is bidirectional. symmetrical=false allows the relationship to be different depending on the direction you're coming from
    owner=models.CharField(max_length=50,blank=True,null=True)#name of person who contents of image belong to
    location=models.ForeignKey(City,blank=True,on_delete=models.SET_NULL,null=True,related_name='image_city')

    # need to add a field for the event. it should be searchable here for the exact name (lVO 2020 vs LVO 2022) but also contains a link to the league page
    #linking to season should acomplish all that
    source=models.ForeignKey(Season,blank=True,null=True,on_delete=models.SET_NULL,related_name='image_source')

    popularity = models.ManyToManyField(User,blank=True,related_name='liked_images')
    uploader=models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
    fuzzy_tags=models.CharField(max_length=1000,default='')

    def __str__(self):
        return self.image_title

    #need this to return to detail view after saving (upload edit)
    def get_absolute_url(self):
        return reverse('image details',kwargs={'pk':self.pk})

class UserSubImage(models.Model):

    image = models.ImageField(upload_to=sub_get_upload_to())
    image_title=models.CharField(max_length=50)
    parent_image=models.ForeignKey(UserImage,on_delete=models.CASCADE,related_name='sub_image')

    def __str__(self):
        return self.image_title
    def get_absolute_url(self):
        return reverse('image details',self.parent_image.pk)
