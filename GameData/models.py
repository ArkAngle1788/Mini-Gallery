from django.db import models
from django.urls import reverse
# from League.models import PlayerSeasonFaction


class Game(models.Model):
    """Game is the top level system identifier"""
    game_system_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return str(self.game_system_name)

    def get_absolute_url(self):
        """
        returns 'manage image fields
        We return this location b/c it's the page you can add other game details
        '"""
        return reverse('manage image fields')
    



class FactionType(models.Model):
    """FactionTypes are children of Game"""
    system = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='game_faction_types')
    faction_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.faction_name+" ("+str(self.system)+")"

    def simple_string(self):
        """
        returns the name with no additional context information
        """
        return str(self.faction_name)

    def get_absolute_url(self):
        """returns 'manage image fields'"""
        return reverse('manage image fields')


class Faction(models.Model):
    """factions are children of FactionType"""
    faction_type = models.ForeignKey(
        FactionType, on_delete=models.CASCADE, related_name='faction_types_factions')
    faction_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.faction_name+" ("+self.faction_type.simple_string()+")"

    def simple_string(self):
        """
        returns the name with no additional context information
        """
        return str(self.faction_name)

    def get_absolute_url(self):
        """returns 'manage image fields'"""
        return reverse('manage image fields')


class SubFaction(models.Model):
    """
    subfactions are children of factions
    vars: faction, faction_name
    """

    faction = models.ForeignKey(
        Faction, on_delete=models.CASCADE, related_name='faction_sub_faction')
    faction_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        if self.faction.faction_name == self.faction_name:
            return self.faction_name
        return self.faction_name+" ["+str(self.faction.simple_string())+"]"

    def simple_string(self):
        """
        returns the name with no additional context information
        """
        return str(self.faction_name)

    def get_absolute_url(self):
        """returns 'manage image fields'"""
        return reverse('manage image fields')


class UnitType(models.Model):
    """
    UnitType currently only links to system
    """
    system = models.ForeignKey(Game, on_delete=models.CASCADE)


    faction=models.ManyToManyField(Faction,blank=True,related_name='unit_faction')
    sub_faction=models.ManyToManyField(
        SubFaction,blank=True,related_name='unit_subfaction')

    unit_type = models.CharField(max_length=100)


    def __str__(self):
        output=self.unit_type
        data=self.get_specific_faction()
        if not data:
            return output
        for entry in self.get_specific_faction():
            output+=" ("+str(entry.simple_string())+")"
        return output

    def simple_string(self):
        """
        returns the name with no additional context information
        """
        return str(self.unit_type)

    def get_specific_faction(self):
        """
        returns the most specific faction type (subfaction/faction)
        or none if neither are defined
        """
        if self.sub_faction.all():
            return self.sub_faction.all()
        if self.faction.all():
            return self.faction.all()
        return None

    def get_absolute_url(self):
        """returns 'manage image fields'"""
        return reverse('manage image fields')


class ArmyList(models.Model):
    psf = models.ForeignKey(
        'League.PlayerSeasonFaction', on_delete=models.CASCADE, related_name='army_lists')
    army_list_name = models.CharField(max_length=25)
    army_list = models.TextField()

    def __str__(self):
        return self.army_list_name

