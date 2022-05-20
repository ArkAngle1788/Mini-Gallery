from django import forms
from .models import *
# from django.forms.widgets import TextInput
from django_select2 import forms as s2forms
from django.forms.widgets import TextInput

factattrs={'class':'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', 'style':'width: 50%','placeholder':'Name or Identifier'}


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
            # 'faction': FactionWidget,
            'faction_name': forms.TextInput(factattrs),
            'system' : GameWidget({'class':'nedsgdsgsdgdsggsdgass', 'style':'width: 90%'}),
        }

class FactionForm(forms.ModelForm):
    class Meta:
        model=Faction
        fields="__all__"
        widgets = {
            'faction_name': forms.TextInput,
            'faction_type' : Faction_TypeWidget({'class':'nedsgdsgsdgdsggsdgass', 'style':'width: 90%'}),
        }



class Sub_FactionForm(forms.ModelForm):
    class Meta:
        model=Sub_Faction
        fields="__all__"
        widgets = {
            # 'faction': FactionWidget,
            'faction_name': forms.TextInput(factattrs),
            'factions' : FactionWidget({'class':'nedsgdsgsdgdsggsdgass', 'style':'width: 90%'}),
        }


class Unit_TypeForm(forms.ModelForm):
    class Meta:
        model=Faction_Type
        fields="__all__"
        widgets = {
            'unit_type': forms.TextInput(factattrs),
            'system' : GameWidget({'class':'nedsgdsgsdgdsggsdgass', 'style':'width: 90%'}),
        }
