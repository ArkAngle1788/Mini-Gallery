from django.db import models
from django.urls import reverse
from GameData.models import Games, Faction, Sub_Faction, Unit_Type
from CommunityInfrastructure.models import City, Region, Country




# UNDER CONSTRUCTION: this file is code fragments from a previous version, it is a mess





#add an location eligibility field for areas to display default registration in ---- maybe not don't want to make the basic configuration too complex and do we really gain that much by doing this?
# league pages need to be visible on the website all the time not just when they're running so that people can look them up and get information about them (because leagues will include events as well)
class League(models.Model):
    league_name = models.CharField(max_length=50) # for example ELD40k-Escalation
    league_description=models.CharField(max_length=600)
    location_city=models.ForeignKey(City,on_delete=models.SET_NULL,null=True,related_name='leagues_in_city')
    display_name=models.BooleanField(default=True)
    # we can use just location_city to tell us everything the following two fields would have told us
    # location_region=models.ForeignKey(Region,on_delete=models.SET_NULL,null=True,related_name='leagues_in_region')
    # location_country=models.ForeignKey(Country,on_delete=models.SET_NULL,null=True,related_name='leagues_in_country')
    system = models.ForeignKey(Games,on_delete=models.CASCADE,related_name='child_leagues')
    def __str__(self):
        return self.league_name

    def get_absolute_url(self):
        return reverse('manage leagues')

# is it best to have the activity flag inside season rather than league?
# the only advantage to season that I can think of is if your season is if you wanted to display information about the next season without opening registration


class Season(models.Model):
    season_name = models.CharField(max_length=50) # for example (ELD40k-Escalation) season 2
    season_active=models.BooleanField(default=False)
    allow_repeat_matches=models.BooleanField(default=False)
    registration_active=models.BooleanField(default=True)
    use_names=models.BooleanField(default=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE,related_name='child_season')
    def __str__(self):
        return str(self.league.league_name)+" "+str(self.season_name)



# depricated phase this out
class Player(models.Model):
    player_name = models.CharField(max_length=50,unique=True)

    def __str__(self):
        return self.player_name
    def get_name(self):
        return self.player_name


class Player_season_faction(models.Model):
    player=models.ForeignKey(Player,on_delete=models.CASCADE,related_name='player_psf')
    faction=models.ForeignKey(Faction,on_delete=models.SET_NULL,null=True,blank=True,related_name='player_faction')
    sub_faction=models.ForeignKey(Sub_Faction,on_delete=models.SET_NULL,null=True,blank=True,related_name='player_sub_faction')
    season=models.ForeignKey(Season,on_delete=models.CASCADE,null=True,blank=True,related_name='player_season')

    # this is updated in save_matchup
    previous_opponents=models.ManyToManyField(Player,blank=True,related_name='previous_opponents')

    score=models.IntegerField(default=0)
    wlrecord=models.CharField(max_length=100,default="-")

    #each time a new round is created this will need to be reset to False
    #right now this should only be looked at for active players so the value can be true from previous rounds as long as it's reset each round
    matched=models.BooleanField(default=False)



    def __str__(self):
        player_name=self.player.get_name()
        season_name=str(self.season)
        # faction_name=str(self.faction)
        title=player_name+"   ------    "+season_name+"   ------   "+str(self.faction)
        if self.sub_faction:
            title=title+"   ------   "+str(self.sub_faction)
        # return player_name#changed this return for a troubleshoot
        return title #admin panel uses this so we want full information



class Round(models.Model):
    round_number = models.IntegerField()
    round_details = models.CharField(max_length=150,default='')
    season=models.ForeignKey(Season,on_delete=models.CASCADE,related_name='seasons_rounds')
    def __str__(self):
        return str(self.season)+" Round "+str((self.round_number))
    def get_absolute_url(self):#this tells us where to go after we directly edit the round info
        url=reverse('manage leagues')
        url+=f"?league={self.season.league.pk}"
        return url

class Match(models.Model):

    round=models.ForeignKey(Round,on_delete=models.CASCADE,related_name='round_matches')

    #confirm that you can have repeat matchups with this setup (pretty sure you can)
    # there is a players played detail attached to player_season_faction
    player1 = models.ForeignKey(Player,on_delete=models.SET_NULL,null=True,blank=True,related_name='player1')
    player2 = models.ForeignKey(Player,on_delete=models.SET_NULL,null=True,blank=True,related_name='player2')
    winner = models.ForeignKey(Player,on_delete=models.SET_NULL,null=True,blank=True,related_name='winner')
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)


    def __str__(self):
        matchup=str(self.round)+": "+str(self.player1)+" vs. "+str(self.player2)
        return matchup
