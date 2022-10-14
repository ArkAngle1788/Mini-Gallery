from django import forms
# from django.contrib.auth import get_user_model
# from django.forms.widgets import TextInput
# from django_select2 import forms as s2forms
from django_select2.forms import Select2Widget

from .models import League

basicattrs = {'class': 'bg-white'}

class LeagueForm(forms.ModelForm):
    """uses all paintng studio fields"""
    class Meta:
        model = League
        fields = ["league_name","league_description","location_city","display_name","system"]
        widgets = {
            'league_name': forms.TextInput(basicattrs),
            'league_description': forms.TextInput(basicattrs),
            'location_city': Select2Widget,
            'display_name': forms.CheckboxInput,
            'system': Select2Widget,
        }


    