from django import forms
from django.db.models import Q
from django_select2.forms import Select2MultipleWidget, Select2Widget
from django.core.validators import ProhibitNullCharactersValidator
from GameData.models import Faction, SubFaction,ArmyList
from UserAccounts.models import AdminProfile,UserProfile
from Gallery.forms import UploadMultipleImages, UploadImagesMultipart
from django.core.exceptions import (ValidationError)

# from django.core.exceptions import ValidationError
from .models import League, Match, PlayerSeasonFaction, Round, Season

basicattrs = {'class': 'bg-white', 'style': 'width:40%'}
default_format = {'style': 'width: 40%'}


class LeagueAdminsWidget(Select2MultipleWidget):
    """searches against names and email"""
    search_fields = [
        "username__icontains",
        "first_name__icontains",
        "last_name__icontains",
        "email__icontains",
    ]


class LeagueForm(forms.ModelForm):
    """
    form for configuring League
    has special logic for selecting managing admins
    """
    admin_list = None

    def __init__(self,  *args, **kwargs):
        group_var = kwargs.pop('group')
        super(LeagueForm, self).__init__(*args, **kwargs)
        self.admin_list = AdminProfile.objects.filter(
            Q(id__in=group_var.group_primary_admins.all())
            |
            Q(id__in=group_var.group_secondary_admins.all())
        )

        self.fields['admin_options'].queryset = self.admin_list

        # if instance will exist on edit but not create
        if kwargs['instance']:
            active_admins = []
            for admin in self.fields['admin_options'].queryset.all():
                if admin in kwargs['instance'].admins_managing.all():
                    active_admins += [admin.id]

            self.initial['admin_options'] = active_admins

    admin_options = forms.ModelMultipleChoiceField(
        queryset=admin_list,
        widget=LeagueAdminsWidget(default_format),
        label="Select Admins")

    class Meta:
        model = League
        fields = ["league_name", "league_description",
                  "location_city", "display_name", "system", "admin_options"]
        widgets = {
            'league_name': forms.TextInput(basicattrs),
            'league_description': forms.TextInput(basicattrs),
            'location_city': Select2Widget,
            'display_name': forms.CheckboxInput,
            'system': Select2Widget,
            'admin_options': LeagueAdminsWidget(default_format),
        }


class SeasonForm(forms.ModelForm):
    """ 4 fields """

    class Meta:
        model = Season
        fields = ["season_name", 'registration_active',
                  "allow_repeat_matches", "registration_key"]
        widgets = {
            'season_name': forms.TextInput(basicattrs),
            'registration_active': forms.CheckboxInput,
            'registration_key': forms.TextInput(basicattrs),
            'allow_repeat_matches': forms.CheckboxInput(),

        }
        help_texts = {
            'allow_repeat_matches': 'If repeat matches are not allowed and there \
                are a odd number of players byes will be available for matchmaking',
        }


class SeasonRegisterForm(forms.ModelForm):
    """ custom logic to only show relevant factons and subfactions """

    registration_key = forms.CharField(
        widget=forms.TextInput(basicattrs),
        help_text="get this code from a league admin")
    faction = forms.ModelChoiceField(
        queryset=None,
        widget=Select2Widget(default_format),
        empty_label=None)
    sub_faction = forms.ModelChoiceField(
        queryset=None,
        widget=Select2Widget(default_format),
        empty_label='',
        help_text="choose if appropriate",
        required=False)



    class Meta:
        model = PlayerSeasonFaction
        fields = ["faction", "sub_faction", "registration_key"]#"army_list",

    def __init__(self,  *args, **kwargs):
        league = kwargs.pop('league')
        super(SeasonRegisterForm, self).__init__(*args, **kwargs)

        self.fields['faction'].queryset = Faction.objects.filter(
            faction_type__system=league.system)
        self.fields['sub_faction'].queryset = SubFaction.objects.filter(
            faction__faction_type__system=league.system)

class PSFUpdateForm(forms.ModelForm):
    """ custom logic to only show relevant factons and subfactions """

    faction = forms.ModelChoiceField(
        queryset=None,
        widget=Select2Widget(default_format),
        empty_label=None)
    sub_faction = forms.ModelChoiceField(
        queryset=None,
        widget=Select2Widget(default_format),
        empty_label='',
        help_text="choose if appropriate",
        required=False)

    class Meta:
        model = PlayerSeasonFaction
        fields = ["faction", "sub_faction"]

    def __init__(self,  *args, **kwargs):
        league = kwargs.pop('league')
        super(PSFUpdateForm, self).__init__(*args, **kwargs)

        self.fields['faction'].queryset = Faction.objects.filter(
            faction_type__system=league.system)
        self.fields['sub_faction'].queryset = SubFaction.objects.filter(
            faction__faction_type__system=league.system)

class DropPlayerChoiceField(forms.ModelChoiceField):
    '''structure copied from base to_python with the try statment changed'''
    widget=Select2MultipleWidget

    def validate_no_null_characters(self, value):
        non_null_character_validator = ProhibitNullCharactersValidator()
        return non_null_character_validator(value)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        self.validate_no_null_characters(value)
        try:
            for key in value:
                PlayerSeasonFaction.objects.get(pk=key)
        except (
            ValueError,
            TypeError,
            self.queryset.model.DoesNotExist,
            ValidationError,
        ):
            raise ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )
        return value

class AddPlayerChoiceField(forms.ModelChoiceField):
    '''structure copied from base to_python with the try statment changed'''
    widget=Select2MultipleWidget
   
    def validate_no_null_characters(self, value):
        non_null_character_validator = ProhibitNullCharactersValidator()
        return non_null_character_validator(value)

    def to_python(self, value):
        if value in self.empty_values:
            return None
        self.validate_no_null_characters(value)
        try:
            for key in value:
                UserProfile.objects.get(pk=key)
        except (
            ValueError,
            TypeError,
            self.queryset.model.DoesNotExist,
            ValidationError,
        ):
            raise ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": value},
            )
        return value

class AddDropPlayerForm(forms.Form):
    """links unit_type to a system"""
    season=None
    drop_players=DropPlayerChoiceField(queryset=PlayerSeasonFaction.objects.filter(pk=5))
    add_players =AddPlayerChoiceField(widget=Select2MultipleWidget,queryset=UserProfile.objects.filter(pk=5))

    def __init__(self,  *args, **kwargs):
        self.season = kwargs.pop('season')
        super(AddDropPlayerForm, self).__init__(*args, **kwargs)

        self.fields['drop_players'].required = False
        self.fields['add_players'].required = False
        self.fields['drop_players'].queryset = PlayerSeasonFaction.objects.filter(season=self.season).exclude(profile__user__username='Tie').exclude(profile__user__username='Bye').exclude(dropped=True)
        self.fields['add_players'].queryset = UserProfile.objects.exclude(psf__season=self.season,psf__dropped=False).exclude(user__username='Tie').exclude(user__username='Bye')

    def clean_drop_players(self):
        """makes sure selected players are in the league"""
        if self.cleaned_data["drop_players"] is None:
            return self.cleaned_data["drop_players"]
        valid_player_options=PlayerSeasonFaction.objects.filter(season=self.season).exclude(profile__user__username='Tie').exclude(profile__user__username='Bye').exclude(dropped=True)
        for psf in self.cleaned_data["drop_players"]:
            psf_object=PlayerSeasonFaction.objects.get(pk=psf)
            if not psf_object in valid_player_options:
                raise ValidationError("Selection is not valid")
        return self.cleaned_data["drop_players"]

    def clean_add_players(self):
        """makes sure selected players are not in the league"""
        if self.cleaned_data["add_players"] is None:
            return self.cleaned_data["add_players"]
        valid_player_options=UserProfile.objects.exclude(psf__season=self.season,psf__dropped=False).exclude(user__username='Tie').exclude(user__username='Bye')
        for user in self.cleaned_data["add_players"]:
            user_object=UserProfile.objects.get(pk=user)
            if not user_object in valid_player_options:
                raise ValidationError("Selection is not valid")
        return self.cleaned_data["add_players"]


class RoundForm(forms.ModelForm):
    """ description only """
    automate_matchmaking = forms.BooleanField(
        widget=forms.CheckboxInput(),help_text="If you want to manually assign\
              a pairing for a Bye match do not use this option.\
                  Instead manually create the bye matchup first then select \
                    automate from the sidebar", required=False)

    class Meta:
        model = Round
        fields = ["round_details"]
        widgets = {
            'round_details': forms.TextInput(basicattrs),
        }

class MatchForm(forms.ModelForm):
    """ excludes tie from options """

    class Meta:
        model = Match
        fields = ["player1", "player2"]
        widgets = {
            'player1': Select2Widget,
            'player2': Select2Widget,
        }

    def __init__(self,  *args, **kwargs):
        season = kwargs.pop('season')
        super(MatchForm, self).__init__(*args, **kwargs)

        self.fields['player1'].queryset = PlayerSeasonFaction.objects.filter(
            season=season).filter(matched=False).exclude(profile__user__username='Tie').exclude(
        dropped=True).exclude(matched=True)
        self.fields['player2'].queryset = PlayerSeasonFaction.objects.filter(
            season=season).filter(matched=False).exclude(profile__user__username='Tie').exclude(
        dropped=True).exclude(matched=True)



def score_constraint_check(self,score_list):
    """
    returns None if constraints are met
    returns string for the validation error if constraints fail
    """
    if self.instance.round.season.league.system.game_system_name=="Infinity":
        datalist = score_list.split(',')
        if len(datalist) != 2:
            return "Infinity Scores should be in the format: OP,VP"
        return None
    return "Game System Does not have scoring Implemented"



class MatchEditForm(forms.ModelForm):
    """ only allows players and tiepsf from match """

    player1_name = 'player1'
    player2_name = 'player2'

    class Meta:
        model = Match
        fields = ["winner", "player1_score", "player2_score","player1_list","player2_list"]
        widgets = {
            'winner': Select2Widget,
            'player1_score': forms.TextInput(basicattrs),
            'player2_score': forms.TextInput(basicattrs),
        }

    def __init__(self,  *args, **kwargs):

        
        player1 = kwargs.pop('player1')
        player2 = kwargs.pop('player2')
        tie_psf = PlayerSeasonFaction.objects.get(
            profile__user__username='Tie', season=player1.season)

        # print('form :')
        # print(args)
        # print(kwargs)
        super(MatchEditForm, self).__init__(*args, **kwargs)
        self.fields['winner'].required = True
        self.fields['player1_score'].label = player1.profile
        # print(self.fields['player1_score'].__dict__)
        self.fields['player2_score'].label = player2.profile
        self.fields['winner'].queryset = PlayerSeasonFaction.objects.filter(
            Q(id=player1.id)
            |
            Q(id=player2.id)
            |
            Q(id=tie_psf.id)
        )
        self.fields['player1_list'].queryset = ArmyList.objects.filter(psf=player1)
        self.fields['player2_list'].queryset = ArmyList.objects.filter(psf=player2)


    def clean_player1_score(self):
        """makes sure the score list has the right number of entries for the system"""
        result=score_constraint_check(self,self.cleaned_data["player1_score"])
        if result:
            raise ValidationError(result)
        return self.cleaned_data["player1_score"]

    def clean_player2_score(self):
        """makes sure the score list has the right number of entries for the system"""
        result=score_constraint_check(self,self.cleaned_data["player2_score"])
        if result:
            raise ValidationError(result)
        return self.cleaned_data["player2_score"]

class MatchUploadMultipleImages(UploadMultipleImages):
    """source is auto assigned"""

    def __init__(self,  *args, **kwargs):
        season_var = kwargs.pop('source')
        super(MatchUploadMultipleImages, self).__init__(*args, **kwargs)

        self.initial['source'] = season_var.pk

class MatchUploadMultipartImages(UploadImagesMultipart):
    """source is auto assigned"""
    def __init__(self,  *args, **kwargs):
        season_var = kwargs.pop('source')
        super(MatchUploadMultipartImages, self).__init__(*args, **kwargs)

        self.initial['source'] = season_var.pk
