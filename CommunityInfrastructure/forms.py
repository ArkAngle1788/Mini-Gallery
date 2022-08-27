from django import forms
from django.contrib.auth import get_user_model
# from django.forms.widgets import TextInput
from django_select2 import forms as s2forms

from CommunityInfrastructure.models import City, Country
from CommunityInfrastructure.models import Group as CIgroup
from CommunityInfrastructure.models import PaintingStudio, Region

# from django_select2.forms import Select2Widget,Select2MultipleWidget



basicattrs = {'class': 'bg-white'}
default_format = {'style': 'width: 90%'}

providers = [('Facebook', 'Facebook'), ('Instagram', 'Instagram')]
# allow up to 10 images because of API limitations
num = [(1, '1'), (2, '2'), (3, "3"), (4, "4"), (5, '5'),
       (6, '6'), (7, '7'), (8, '8'), (9, '9'), (10, '10')]


class SelectExport(forms.Form):
    """10 images b/c of api limitations. providers is defined here in forms.py"""
    select_number = forms.ChoiceField(
        choices=num, widget=forms.Select(basicattrs))
    platform = forms.ChoiceField(
        choices=providers, widget=forms.Select(basicattrs))

    # icontains is the default so this is more of a functionality/syntax reference
    # when these might be useful for more complex lookups if unit_type is changed to link factions
    # or if we want only unit types from a selected system to show up or such.


class GameWidget(s2forms.Select2Widget):
    """searches against name"""
    search_fields = [
        'game_system_name__icontains',
    ]


class FactionWidget(s2forms.Select2Widget):
    """searches against name"""
    search_fields = [
        'faction_name__icontains',
    ]


class CityWidget(s2forms.Select2Widget):
    """searches against name"""
    search_fields = [
        'city_name__icontains',
    ]


class RegionWidget(s2forms.Select2Widget):
    """searches against name"""
    search_fields = [
        'region_name__icontains',
    ]


class CountryWidget(s2forms.Select2Widget):
    """searches against name"""
    search_fields = [
        'country_name__icontains',
    ]


class ProfileWidget(s2forms.ModelSelect2Widget):
    """searches against username and email"""
    search_fields = [
        "username__icontains",
        "email__icontains",
    ]


class UnapprovedUsersWidget(s2forms.ModelSelect2Widget):
    """searches against names and email"""
    search_fields = [
        "username__icontains",
        "first_name__icontains",
        "last_name__icontains",
        "email__icontains",
    ]


class ApproveUserForm(forms.Form):
    """selects from all users that do not have the add_userimage permission"""
    unapproved_user = forms.ModelChoiceField(
        queryset=get_user_model().objects.all().exclude(
            groups__permissions__codename="add_userimage"),
        widget=UnapprovedUsersWidget(default_format))


class GroupForm(forms.ModelForm):
    """
    fields are: 'group_name','group_tag','group_description',
    'location_city','location_region','location_country'
    """
    class Meta:
        model = CIgroup
        fields = ['group_name', 'group_tag', 'group_description',
                  'location_city', 'location_region', 'location_country']
        widgets = {
            'group_name': forms.TextInput(basicattrs),
            'group_tag': forms.TextInput(basicattrs),
            'group_description': forms.TextInput(basicattrs),
            'location_city': CityWidget,
            'location_region': RegionWidget,
            'location_country': CountryWidget,
        }


class StudioForm(forms.ModelForm):
    """uses all paintng studio fields"""
    class Meta:
        model = PaintingStudio
        fields = "__all__"
        widgets = {
            'Studio_name': forms.TextInput(basicattrs),
            'Studio_page': forms.TextInput(basicattrs),
            'description': forms.TextInput(basicattrs),
            'location': CityWidget,
            'userprofile': ProfileWidget(default_format),
        }


class CountryForm(forms.ModelForm):
    """fields are country_name"""
    class Meta:
        model = Country
        fields = "__all__"
        widgets = {
            'country_name': forms.TextInput(basicattrs),
        }


class RegionForm(forms.ModelForm):
    """fields are country, region_name"""
    class Meta:
        model = Region
        fields = "__all__"
        widgets = {
            'country': CountryWidget,
            'region_name': forms.TextInput(basicattrs),
        }


class CityForm(forms.ModelForm):
    """fields are region, city_name"""
    class Meta:
        model = City
        fields = "__all__"
        widgets = {
            'region': RegionWidget,
            'city_name': forms.TextInput(basicattrs),
        }
