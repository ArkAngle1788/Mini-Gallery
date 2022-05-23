from django import forms
from CommunityInfrastructure.models import Country, Region, City, PaintingStudio
from CommunityInfrastructure.models import Group as CIgroup
# from django.forms.widgets import TextInput
from django_select2 import forms as s2forms
from django.forms.widgets import TextInput

basicattrs={'class':'bg-white'}
default_format={'style':'width: 90%'}

providers=[('Facebook','Facebook'),('Instagram','Instagram')]
num=[(1,'1'),(2,2),(3,"3"),(4,"4"),(5,'5'),(6,'6'),(7,7),(8,8),(9,9),(10,10)]#these all appear the same when rendered in the final form

class SelectExport(forms.Form):
    select_number=forms.ChoiceField(choices=num,widget=forms.Select(basicattrs))
    platform=forms.ChoiceField(choices=providers,widget=forms.Select(basicattrs))
    # class Meta:
    #     fields="__all__"

class GameWidget(s2forms.Select2Widget):
    #do these even do anything? they might not for a basic select widget i should test that sometime....
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
            'group_name':forms.TextInput(basicattrs),
            'group_tag':forms.TextInput(basicattrs),
            'group_description':forms.TextInput(basicattrs),
            'location_city': City_Widget,
            'location_region': Region_Widget,
            'location_country': Country_Widget,
        }

class Studio_Form(forms.ModelForm):
    class Meta:
        model=PaintingStudio
        fields="__all__"
        widgets = {
            'Studio_name':forms.TextInput(basicattrs),
            'Studio_page':forms.TextInput(basicattrs),
            'description':forms.TextInput(basicattrs),
            'location': City_Widget,
            'userprofile': Profile_Widget(default_format),
        }

class Country_Form(forms.ModelForm):
    class Meta:
        model=Country
        fields="__all__"
        widgets = {
            'country_name': forms.TextInput(basicattrs),
        }

class Region_Form(forms.ModelForm):
    class Meta:
        model=Region
        fields="__all__"
        widgets = {
            'country': Country_Widget,
            'region_name':forms.TextInput(basicattrs),
        }
class City_Form(forms.ModelForm):
    class Meta:
        model=City
        fields="__all__"
        widgets = {
            'region': Region_Widget,
            'city_name':forms.TextInput(basicattrs),
        }
