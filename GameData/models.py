from django.db import models
from django.urls import reverse

class Games(models.Model):
    game_system_name = models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.game_system_name
    def get_absolute_url(self):
        return reverse('manage image fields')

class Faction_Type(models.Model):
    system=models.ForeignKey(Games,on_delete=models.CASCADE,related_name='game_faction_types')
    faction_name=models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.faction_name
    def get_absolute_url(self):
        return reverse('manage image fields')

class Faction(models.Model):
    faction_type=models.ForeignKey(Faction_Type,on_delete=models.CASCADE,related_name='faction_types_factions')
    faction_name=models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.faction_name
    def get_absolute_url(self):
        return reverse('manage image fields')

class Sub_Faction(models.Model):
    factions=models.ForeignKey(Faction,on_delete=models.CASCADE,related_name='faction_sub_faction')
    faction_name=models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.faction_name
    def get_absolute_url(self):
        return reverse('manage image fields')

class Unit_Type(models.Model):
    system = models.ForeignKey(Games,on_delete=models.CASCADE)
    # getting this detailed would be nice but it depends on how easily we can dynamically adjust filtering options to take advantage of this level of detail
    # factions=models.ManyToManyField(Faction,blank=True,related_name='factions_unit_type')
    # can we get away with just defining a subfaction (select all in most cases) and then reverse lookup to find something like 'all eldar units'
    # sub_factions=models.ManyToManyField(Sub_Faction,blank=True,related_name='sub_factions_unit_type')
    unit_type = models.CharField(max_length=100,unique=True)
    def __str__(self):
        return self.unit_type
    def get_absolute_url(self):
        return reverse('manage image fields')
