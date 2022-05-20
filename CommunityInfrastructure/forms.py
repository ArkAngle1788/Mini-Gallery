from django import forms
from CommunityInfrastructure.models import Country, Region, City, PaintingStudio
from CommunityInfrastructure.models import Group as CIgroup
# from django.forms.widgets import TextInput
from django_select2 import forms as s2forms
from django.forms.widgets import TextInput

default_format={'style':'width: 90%'}

providers=[('Facebook','Facebook'),('Instagram','Instagram')]
num=[(1,'1'),(2,2),(3,"3"),(4,"4"),(5,'5'),(6,'6'),(7,7),(8,8),(9,9),(10,10)]#these all appear the same when rendered in the final form

class SelectExport(forms.Form):
    select_number=forms.ChoiceField(choices=num)
    platform=forms.ChoiceField(choices=providers)
    # class Meta:
    #     fields="__all__"

class GameWidget(s2forms.Select2Widget):
    search_fields=[
        'game_system_name__icontains',
    ]

class FactionWidget(s2forms.Select2Widget):
    search_fields=[
        'faction_name__icontains',
    ]


class City_Widget(s2forms.Select2Widget):
    search_fields=[
        'city_name__icontains',
    ]
class Region_Widget(s2forms.Select2Widget):
    search_fields=[
        'region_name__icontains',
    ]
class Country_Widget(s2forms.Select2Widget):
    search_fields=[
        'country_name__icontains',
    ]
class Profile_Widget(s2forms.ModelSelect2Widget):
    search_fields = [
        "username__icontains",
        "email__icontains",
    ]


class Group_Form(forms.ModelForm):
    class Meta:
        model=CIgroup
        fields=['group_name','group_tag','group_description','location_city','location_region','location_country']
        widgets = {
            'location_city': City_Widget,
            'location_region': Region_Widget,
            'location_country': Country_Widget,
        }

class Studio_Form(forms.ModelForm):
    class Meta:
        model=PaintingStudio
        fields="__all__"
        widgets = {
            'location': City_Widget,
            'userprofile': Profile_Widget(default_format),
        }
class Region_Form(forms.ModelForm):
    class Meta:
        model=Region
        fields="__all__"
        widgets = {
            'country': Country_Widget,
        }
class City_Form(forms.ModelForm):
    class Meta:
        model=City
        fields="__all__"
        widgets = {
            'region': Region_Widget,
        }
#
# class FactionForm(forms.ModelForm):
#     class Meta:
#         model=Faction
#         fields="__all__"
#         widgets = {
#             'faction_name': forms.TextInput,
#             'faction_type' : Faction_TypeWidget({'class':'nedsgdsgsdgdsggsdgass', 'style':'width: 90%'}),
#         }
#
#
#
# class Sub_FactionForm(forms.ModelForm):
#     class Meta:
#         model=Sub_Faction
#         fields="__all__"
#         widgets = {
#             # 'faction': FactionWidget,
#             'faction_name': forms.TextInput(factattrs),
#             'factions' : FactionWidget({'class':'nedsgdsgsdgdsggsdgass', 'style':'width: 90%'}),
#         }
#
#
# class Unit_TypeForm(forms.ModelForm):
#     class Meta:
#         model=Faction_Type
#         fields="__all__"
#         widgets = {
#             'unit_type': forms.TextInput(factattrs),
#             'system' : GameWidget({'class':'nedsgdsgsdgdsggsdgass', 'style':'width: 90%'}),
#         }
