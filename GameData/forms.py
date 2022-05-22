from django import forms
from .models import *
# from django.forms.widgets import TextInput
from django_select2 import forms as s2forms
from django.forms.widgets import TextInput


basicattrs={'style':'width: 90%'}#select2 can only have limited styling applied to it with classes. to substantially change it it looks like we would need to override the select2 css classes

textfieldattrs=basicattrs.copy()
textfieldattrs['class']='bg-white'
textfieldattrs['placeholder']='input'

print(basicattrs)
print(f"\n\n{textfieldattrs}\n\n")

class GameWidget(s2forms.Select2Widget):
    search_fields=[
        'game_system_name__icontains',
    ]

class FactionWidget(s2forms.Select2Widget):
    search_fields=[
        'faction_name__icontains',
    ]


class Faction_TypeWidget(s2forms.Select2Widget):
    search_fields=[
        'faction_name__icontains',
    ]

# class testwidget(forms.TextInput):


class SystemForm(forms.ModelForm):
    class Meta:
        model=Games
        fields="__all__"
        widgets = {
            'game_system_name': forms.TextInput,
        }

class Faction_TypeForm(forms.ModelForm):
    class Meta:
        model=Faction_Type
        fields="__all__"
        widgets = {
            'system' : GameWidget(basicattrs),
            'faction_name': forms.TextInput(textfieldattrs),

        }

class FactionForm(forms.ModelForm):
    class Meta:
        model=Faction
        fields="__all__"
        widgets = {
            'faction_type' : Faction_TypeWidget(basicattrs),
            'faction_name': forms.TextInput(textfieldattrs),
        }



class Sub_FactionForm(forms.ModelForm):
    class Meta:
        model=Sub_Faction
        fields="__all__"
        widgets = {
            'factions' : FactionWidget(basicattrs),
            'faction_name': forms.TextInput(textfieldattrs),
        }


class Unit_TypeForm(forms.ModelForm):
    class Meta:
        model=Unit_Type
        fields="__all__"
        widgets = {
            'system' : GameWidget(basicattrs),
            'unit_type': forms.TextInput(textfieldattrs),
        }
