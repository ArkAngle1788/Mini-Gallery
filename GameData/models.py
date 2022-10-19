from django.db import models
from django.urls import reverse


class Game(models.Model):
    """Game is the top level system identifier"""
    game_system_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.game_system_name

    def get_absolute_url(self):
        """returns 'manage image fields'"""
        return reverse('manage image fields')


class FactionType(models.Model):
    """FactionTypes are children of Game"""
    system = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='game_faction_types')
    faction_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.faction_name

    def get_absolute_url(self):
        """returns 'manage image fields'"""
        return reverse('manage image fields')


class Faction(models.Model):
    """factions are children of FactionType"""
    faction_type = models.ForeignKey(
        FactionType, on_delete=models.CASCADE, related_name='faction_types_factions')
    faction_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.faction_name

    def get_absolute_url(self):
        """returns 'manage image fields'"""
        return reverse('manage image fields')


class SubFaction(models.Model):
    """subfactions are children of factions"""

    faction = models.ForeignKey(
        Faction, on_delete=models.CASCADE, related_name='faction_sub_faction')
    faction_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.faction_name

    def get_absolute_url(self):
        """returns 'manage image fields'"""
        return reverse('manage image fields')


class UnitType(models.Model):
    """
    UnitType currently only links to system
    """
    system = models.ForeignKey(Game, on_delete=models.CASCADE)
    # getting this detailed would be nice but it depends on how easily
    # we can dynamically adjust filtering options
    # to take advantage of this level of detail

    unit_type = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.unit_type

    def get_absolute_url(self):
        """returns 'manage image fields'"""
        return reverse('manage image fields')
