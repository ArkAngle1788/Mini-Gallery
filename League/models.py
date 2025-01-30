# from django.core.validators import int_list_validator
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
# from django.core.exceptions import ValidationError
from CommunityInfrastructure.models import City, Group, validate_int_list
from GameData.models import Faction, Game, SubFaction,ArmyList

# from UserAccounts.models import UserProfile

# UNDER CONSTRUCTION: this file is code fragments from a previous version, it is a mess


# add a location eligibility field for areas to display default registration in
# ---- maybe not don't want to make the basic configuration too complex
# and do we really gain that much by doing this?

# league pages need to be visible on the website all the time not just when they're running so
# that people can look them up and get information about them
# (because leagues will include events as well)
class League(models.Model):
    """
    leagues are persistant between seasons
    as the meta gameplay organization container for groups
    """
    # for example ELD40k-Escalation
    league_name = models.CharField(max_length=50)
    league_description = models.CharField(max_length=600)
    location_city = models.ForeignKey(
        City, on_delete=models.SET_NULL, null=True, related_name='leagues_in_city')
    display_name = models.BooleanField(default=True)
    system = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='child_leagues')
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="leagues_managed")

    def __str__(self):
        return self.league_name

    def get_absolute_url(self):
        """returns 'league details'"""
        return reverse('league details',
            kwargs={'league': slugify(self.league_name), 'pk': self.pk})


class Season(models.Model):
    """a season has a maximum number of rounds if repeat machups are not allowed"""
    # for example (ELD40k-Escalation) season 2
    season_name = models.CharField(max_length=50)
    scoring_instructions = models.CharField(max_length=1000)
    season_active = models.BooleanField(default=False)
    allow_repeat_matches = models.BooleanField(default=False)
    registration_active = models.BooleanField(default=True)
    registration_key = models.CharField(max_length=10)
    # use_names = models.BooleanField(default=True)
    qr_code_key=models.CharField(max_length=10,unique=True,null=True)
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name='child_season')

    def __str__(self):
        return str(self.league.league_name) + " " + str(self.season_name)
    def concise_str(self):
        """a cleaner string that only has the season name"""
        return str(self.season_name)

    def get_absolute_url(self):
        """returns 'season details'"""
        return reverse('season details',
            kwargs={'league': slugify(self.league.league_name), 'pk': self.pk})


class PlayerSeasonFaction(models.Model):
    """
    tracks season information for a player including score
    profile,faction,sub_faction,season,army_list,previous_opponents,score,wlrecord,matched
    """
    profile = models.ForeignKey(
        'UserAccounts.UserProfile', on_delete=models.CASCADE, related_name='psf')
    faction = models.ForeignKey(Faction, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='player_faction')
    sub_faction = models.ForeignKey(SubFaction, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='player_sub_faction')
    season = models.ForeignKey(Season, on_delete=models.CASCADE,
                               null=True, blank=True, related_name='players_in_season')

    # army_list = models.ForeignKey(ArmyList,on_delete=models.CASCADE,
    #                               null=True,blank=True, related_name='list_owner')

    # next four variables are updated in round_create
    # previous_opponents = models.ManyToManyField(
    #     'League.PlayerSeasonFaction', blank=True, related_name='previous_opponents')
    previous_opponents=models.ManyToManyField("self",blank=True)


    # new_score = models.CharField(validators=int_list_validator)
    #score = models.IntegerField(default=0)# when score is calculated it could also generate additional score related fields (victory points against)
    #also could have a signal implemented so that when PSF or matches are updated the score is recalculated so editing the score in a match will auto correct a psf score (could probably get rid of round close score updating using this method)
    
    score=models.CharField(
        max_length=20,default='0,0,0,0,0,0,0', null=True,blank=True, validators=[validate_int_list])
    internal_score=models.PositiveBigIntegerField(default=0)#if scores can be longer than 4 digets the logic needs to be updated for calculating this value
    
    wlrecord = models.CharField(max_length=100, default="-")

    # each time a new round is created this will need to be reset to False
    # right now this should only be looked at for active players so the
    # value can be true from previous rounds as long as it's reset each round (currently reset when match saves)
    # theoretically if you saved a match while auto matchmaking was happening that could break things
    matched = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        
        self.wlrecord='-'
        score_list=self.score.split(',')
        self.internal_score=0
        # print((Match.objects.filter(round__season=self.season,player1__pk=self.pk)|Match.objects.filter(round__season=self.season,player2__pk=self.pk)).order_by('id'))
        for match in (Match.objects.filter(round__season=self.season,player1__pk=self.pk)|Match.objects.filter(round__season=self.season,player2__pk=self.pk)).order_by('id'):
            if match.winner:#an active season can have a current round where winner is still null
                if match.winner.pk == self.pk:
                    self.wlrecord += "W-"
                elif match.winner.profile.user.username == 'Tie':
                    self.wlrecord += "T-"
                else:
                    self.wlrecord += "L-"


        # this could also be in match save with the score calculations but I'm putting it here now for simplicity's sake.
        # we could alternativly calculate this by adding or subtracting scores applying game specific modifiers in match save but this is much less lines of code since it all fits in a system agnostic loop
        num_score=0
        score_multiplyer=1
        for score_component in reversed(score_list):
            num_score+=int(score_component)*score_multiplyer
            score_multiplyer*=10000
        # print(f'matchmaking score is : {num_score}')
        self.internal_score=num_score


        super().save(*args, **kwargs)#update model






    def __str__(self):
        player_name = str(self.profile.user)
        season_name = str(self.season)
        faction_name = str(self.faction)
        title = player_name + "   ------    " + \
            season_name + "   ------   " + faction_name
        if self.sub_faction:
            title = title + "   ------   " + str(self.sub_faction)

        # admin panel uses this so we want full information
        return title
    def concise_str(self):
        """prints less verbose PSF info"""
        player_name = str(self.profile.user)
        season_name = str(self.season.concise_str())
        faction_name = str(self.faction)
        title = player_name + "   ------    " + \
            season_name + "   ------   " + faction_name
        if self.sub_faction:
            title = title + "   ------   " + str(self.sub_faction)

        return title
    
    def print_most_specific_faction(self):
        """
        easily displays the most specific type of faction selected
        """
        if self.sub_faction:
            title = str(self.sub_faction)
        else:
            title = str(self.faction)
        return title

    def get_absolute_url(self):
        """returns 'season details'"""
        return reverse('season details',
            kwargs={'league': slugify(self.season.league.league_name), 'pk': self.season.pk})


class Round(models.Model):
    """
    rounds consist of matches populated by all players
    round_number is tracked to make displaying the round easy
    """
    round_number = models.IntegerField()
    round_details = models.CharField(max_length=250, default='')
    season = models.ForeignKey(
        Season, on_delete=models.CASCADE, related_name='seasons_rounds')

    def __str__(self):
        return str(self.season) + " Round " + str((self.round_number))
    def concise_str(self):
        """prints Round X"""
        return "Round " + str((self.round_number))

    # this tells us where to go after we directly edit the round info
    def get_absolute_url(self):
        """returns 'round details'"""
        return reverse('round details',
            kwargs={'league': slugify(self.season.league.league_name), 'pk': self.pk})


class Match(models.Model):
    """contains the player and scoring details of a gameplay instance"""
    round = models.ForeignKey(
        Round, on_delete=models.CASCADE, related_name='round_matches')

    player1 = models.ForeignKey(
        PlayerSeasonFaction, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='player1')
    player2 = models.ForeignKey(
        PlayerSeasonFaction, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='player2')
    winner = models.ForeignKey(
        PlayerSeasonFaction, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='winner')
    

    player1_score = models.CharField(
        max_length=20,default='0,0,0,0,0,0,0', null=True,blank=True, validators=[validate_int_list])
    player2_score = models.CharField(
        max_length=20,default='0,0,0,0,0,0,0', null=True,blank=True, validators=[validate_int_list])
    
    player1_list=models.ForeignKey(
        ArmyList,on_delete=models.SET_NULL,
        null=True,blank=True,related_name='p1_list_in_match'
    )
    player2_list=models.ForeignKey(
        ArmyList,on_delete=models.SET_NULL,
        null=True,blank=True,related_name='p2_list_in_match'
    )

    def __str__(self):

        if self.round.season.league.display_name:
            matchup = str(self.round) + ": " + str(self.player1) + \
                " vs. " + str(self.player2)
        else:
            matchup = str(self.round) + ": " + str(self.player1.profile) + \
                " vs. " + str(self.player2.profile)
        return matchup
    

    def save(self, *args, **kwargs):
        if self.pk:#save old values
            # print(self.pk)
            match=Match.objects.get(pk=self.pk)
            previous_player1_score = match.player1_score
            previous_player2_score = match.player2_score
            # previous_winner=match.winner
            # since there's a model validator on the list format it's safe to trust the split
            previous_player1_score_list = previous_player1_score.split(',')
            player1_score_list = self.player1_score.split(',')
            previous_player2_score_list = previous_player2_score.split(',')
            player2_score_list = self.player2_score.split(',')
            

            if self.round.season.league.system.game_system_name=="Infinity":
                # calculate objective points
                p1_objective_points=int(player1_score_list[0])
                p2_objective_points=int(player2_score_list[0])
                p1_tournament_points=0
                p2_tournament_points=0

                bye_player=PlayerSeasonFaction.objects.filter(profile__user__username = "Bye")
                if self.player1==bye_player or self.player2==bye_player:
                    if self.player1==bye_player:
                        p2_tournament_points=4
                    if self.player2==bye_player:
                        p1_tournament_points=4
                else:
                    if (p1_objective_points-p2_objective_points)>0:
                        # earn 4 p1
                        p1_tournament_points=4
                        if p1_objective_points>=5:
                            # earn +1 p1
                            p1_tournament_points+=1
                        if p1_objective_points-p2_objective_points <=2:
                            # earn +1 p2
                            p2_tournament_points+=1
                    elif (p1_objective_points-p2_objective_points)==0:
                        # earn 2 both
                        p1_tournament_points=2
                        p2_tournament_points=2
                        # missions might be designed to score such that it's impossible for both players to get 5+ but this covers unusual custom missions
                        if p2_objective_points>=5:
                            # earn +1 p2
                            p2_tournament_points+=1
                        if p1_objective_points>=5:
                            # earn +1 p1
                            p1_tournament_points+=1
                    elif (p1_objective_points-p2_objective_points)<0:
                        # earn 4 p2
                        p2_tournament_points=4
                        if p2_objective_points>=5:
                            # earn +1 p2
                            p2_tournament_points+=1
                        if p2_objective_points-p1_objective_points<=2:
                            # earn +1 p1
                            p1_tournament_points+=1
                self.player1_score =f'{p1_tournament_points},{int(player1_score_list[0])},{int(player1_score_list[1])}'
                self.player2_score =f'{p2_tournament_points},{int(player2_score_list[0])},{int(player2_score_list[1])}'
                player1_score_list = self.player1_score.split(',')
                player2_score_list = self.player2_score.split(',')
                    # Victory 4 Earning more Objective Points than the opponent.
                    # Tie 2 Earning as many Objective Points as the opponent.
                    # Defeat 0 Earning fewer Objective Points than the opponent.
                    # Offensive Bonus +1 Earning 5 or more Objective Points. This Tournament Point is added to the obtained result.
                    # Defensive Bonus +1 Losing by 2 or less Objective Points. This Tournament Point is added to the obtained result

                    #a bye gives 4 TP and OP/VP calculated at the end of the event


            super().save(*args, **kwargs)#update model
           

            if  (self.player1_score != previous_player1_score) or (self.player2_score != previous_player2_score) :#check for differences
                
                if self.round.season.league.system.game_system_name=="Infinity":
                    

                    dif1=int(player1_score_list[0])-int(previous_player1_score_list[0])
                    dif2=int(player1_score_list[1])-int(previous_player1_score_list[1])
                    dif3=int(player1_score_list[2])-int(previous_player1_score_list[2])

                    total_score_list_p1=self.player1.score.split(',')

                    total_score_list_p1[0]=int(total_score_list_p1[0])+dif1
                    total_score_list_p1[1]=int(total_score_list_p1[1])+dif2
                    total_score_list_p1[2]=int(total_score_list_p1[2])+dif3
                    self.player1.score=f'{total_score_list_p1[0]},{total_score_list_p1[1]},{total_score_list_p1[2]}'

                    

                    dif1=int(player2_score_list[0])-int(previous_player2_score_list[0])
                    dif2=int(player2_score_list[1])-int(previous_player2_score_list[1])
                    dif3=int(player2_score_list[2])-int(previous_player2_score_list[2])

                    total_score_list_p2=self.player2.score.split(',')

                    total_score_list_p2[0]=int(total_score_list_p2[0])+dif1
                    total_score_list_p2[1]=int(total_score_list_p2[1])+dif2
                    total_score_list_p2[2]=int(total_score_list_p2[2])+dif3
                    self.player2.score=f'{total_score_list_p2[0]},{total_score_list_p2[1]},{total_score_list_p2[2]}'




                self.player1.matched = False
                self.player2.matched = False
                self.player1.save()
                self.player2.save()


        super().save(*args, **kwargs)#run normal save if the match is being created for the first time


    def concise_str(self):
        """
        prints name vs. name
        will display username or first name
        """
        if self.round.season.league.display_name:
            matchup = str(self.player1.profile.user.username) + \
                " vs. " + str(self.player2.profile.user.username)
        else:
            matchup = str(self.player1.profile.user.first_name) + \
                " vs. " + str(self.player2.profile.user.first_name)
        return matchup

    def get_absolute_url(self):
        """returns 'round details'"""
        return reverse('round details',
                    kwargs={
                        'league': slugify(self.round.season.league.league_name),
                        'pk': self.round.pk})
