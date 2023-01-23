from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from CommunityInfrastructure.models import City, Group
from GameData.models import Faction, Game, SubFaction

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
    league = models.ForeignKey(
        League, on_delete=models.CASCADE, related_name='child_season')

    def __str__(self):
        return str(self.league.league_name) + " " + str(self.season_name)
    def concise_str(self):
        return str(self.season_name)

    def get_absolute_url(self):
        """returns 'season details'"""
        return reverse('season details',
            kwargs={'league': slugify(self.league.league_name), 'pk': self.pk})


class PlayerSeasonFaction(models.Model):
    """tracks season information for a player including score"""
    profile = models.ForeignKey(
        'UserAccounts.UserProfile', on_delete=models.CASCADE, related_name='psf')
    faction = models.ForeignKey(Faction, on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='player_faction')
    sub_faction = models.ForeignKey(SubFaction, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='player_sub_faction')
    season = models.ForeignKey(Season, on_delete=models.CASCADE,
                               null=True, blank=True, related_name='players_in_season')

    # next four variables are updated in round_create
    # previous_opponents = models.ManyToManyField(
    #     'League.PlayerSeasonFaction', blank=True, related_name='previous_opponents')
    previous_opponents=models.ManyToManyField("self",blank=True)

    score = models.IntegerField(default=0)
    wlrecord = models.CharField(max_length=100, default="-")

    # each time a new round is created this will need to be reset to False
    # right now this should only be looked at for active players so the
    # value can be true from previous rounds as long as it's reset each round (currently reset when creating the next round)
    matched = models.BooleanField(default=False)

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
    player1_score = models.IntegerField(default=0)
    player2_score = models.IntegerField(default=0)

    def __str__(self):

        if self.round.season.league.display_name:
            matchup = str(self.round) + ": " + str(self.player1) + \
                " vs. " + str(self.player2)
        else:
            matchup = str(self.round) + ": " + str(self.player1.profile) + \
                " vs. " + str(self.player2.profile)
        return matchup

    def concise_str(self):
        """prints name vs. name"""
        if self.round.season.league.display_name:
            matchup = str(self.player1.profile.user.username) + \
                " vs. " + str(self.player2.profile.user.username)
        else:
            matchup = str(self.player1.profile) + \
                " vs. " + str(self.player2.profile)
        return matchup

    def get_absolute_url(self):
        """returns 'round details'"""
        return reverse('round details',
                    kwargs={
                        'league': slugify(self.round.season.league.league_name),
                        'pk': self.round.pk})
