
from django import forms
from django_select2.forms import Select2MultipleWidget, Select2Widget

from UserAccounts.models import AdminProfile
from django.core.exceptions import ValidationError
from .models import League
from django.db.models import Q

basicattrs = {'class': 'bg-white'}
default_format = {'style': 'width: 90%'}


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
        group_var=kwargs.pop('group')
        super(LeagueForm, self).__init__(*args, **kwargs)
        # self.admin_list=group_var.group_primary_admins.all()
        # self.admin_list=self.admin_list.union(group_var.group_secondary_admins.all())
        
        # self.admin_list = AdminProfile.objects.filter(id__in=group_var.group_primary_admins.all() or id__in=group_var.group_secondary_admins.all())

        self.admin_list = AdminProfile.objects.filter( Q(id__in=group_var.group_primary_admins.all()) | Q(id__in=group_var.group_secondary_admins.all()))
        # self.admin_list = AdminProfile.objects.all

        self.fields['admin_options'].queryset = self.admin_list

    admin_options = forms.ModelMultipleChoiceField(
        queryset=admin_list, widget=LeagueAdminsWidget(default_format))

    class Meta:
        model = League
        fields = ["league_name","league_description","location_city","display_name","system","admin_options"]
        widgets = {
            'league_name': forms.TextInput(basicattrs),
            'league_description': forms.TextInput(basicattrs),
            'location_city': Select2Widget,
            'display_name': forms.CheckboxInput,
            'system': Select2Widget,
            'admin_options': LeagueAdminsWidget(default_format),
        }

    # def clean_adminoptions(self):
    #     # data = self.cleaned_data['adminoptions']
        
    #     print("\n\nverifying validation overload\n\n")


    #     raise ValidationError("You have forgotten about Fred!")
    #     # Always return a value to use as the new cleaned data, even if
    #     # this method didn't change it.
    #     # return data

