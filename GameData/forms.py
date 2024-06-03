from django import forms
# from django.forms.widgets import TextInput
from django_select2 import forms as s2forms


from .models import Faction, FactionType, Game, SubFaction, UnitType

# select2 can only have limited styling applied to it with classes.
# to substantially change it it looks like
# we would need to override the select2 css classes
basicattrs = {'style': 'width: 90%'}

textfieldattrs = basicattrs.copy()
textfieldattrs['class'] = 'bg-white'
textfieldattrs['placeholder'] = 'input text here'


class GameWidget(s2forms.Select2Widget):
    """name__icontains search, can be adapted"""
    search_fields = [
        'game_system_name__icontains',
    ]


class FactionTypeWidget(s2forms.ModelSelect2Widget):
    """name__icontains search, can be adapted"""
    
    search_fields = [
        'system__game_system_name__icontains',
        'faction_name__icontains',
    ]
    

class FactionWidget(s2forms.ModelSelect2Widget):
    """name__icontains search, can be adapted"""
    search_fields = [
        'faction_type__system__game_system_name__icontains',
        'faction_name__icontains',
    ]


class SystemForm(forms.ModelForm):
    """creates a game system"""
    class Meta:
        model = Game
        fields = "__all__"
        widgets = {
            'game_system_name': forms.TextInput,
        }


class FactionTypeForm(forms.ModelForm):
    """links a type of faction to a game system"""
    class Meta:
        model = FactionType
        fields = "__all__"
        widgets = {
            'system': GameWidget(basicattrs),
            'faction_name': forms.TextInput(textfieldattrs),
        }


class FactionForm(forms.ModelForm):
    """links a faction to it's type"""
    class Meta:
        model = Faction
        fields = "__all__"
        widgets = {
            'faction_type': FactionTypeWidget(basicattrs),
            'faction_name': forms.TextInput(textfieldattrs),
        }


class SubFactionForm(forms.ModelForm):
    """links a subfaction to a faction"""
    class Meta:
        model = SubFaction
        fields = "__all__"
        widgets = {
            'faction': FactionWidget(basicattrs),
            'faction_name': forms.TextInput(textfieldattrs),
        }


class UnitTypeForm(forms.ModelForm):
    """links unit_type to a system"""
    class Meta:
        model = UnitType
        fields = "__all__"
        widgets = {
            'system': GameWidget(basicattrs),
            'unit_type': forms.TextInput(textfieldattrs),
            'sub_faction': s2forms.Select2MultipleWidget,
            'faction': s2forms.Select2MultipleWidget,
        }