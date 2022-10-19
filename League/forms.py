
from django import forms
from django.db.models import Q
from django_select2.forms import Select2MultipleWidget, Select2Widget
from GameData.models import Faction, SubFaction
from UserAccounts.models import AdminProfile

# from django.core.exceptions import ValidationError
from .models import League, PlayerSeasonFaction, Season

basicattrs = {'class': 'bg-white','style':'width:40%'}
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
    """ text """
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
    """ text """

    class Meta:
        model = Season
        fields = ["season_name", "allow_repeat_matches", "registration_key"]
        widgets = {
            'season_name': forms.TextInput(basicattrs),
            'registration_key': forms.TextInput(basicattrs),
            'allow_repeat_matches': forms.CheckboxInput,

        }


class SeasonRegisterForm(forms.ModelForm):
    """ text """

    registration_key= forms.CharField(
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
        fields = ["faction", "sub_faction","registration_key"]

    def __init__(self,  *args, **kwargs):
        league = kwargs.pop('league')
        super(SeasonRegisterForm, self).__init__(*args, **kwargs)

        self.fields['faction'].queryset = Faction.objects.filter(
                                                            faction_type__system=league.system)
        self.fields['sub_faction'].queryset = SubFaction.objects.filter(
                                                                    faction__faction_type__system=league.system)
