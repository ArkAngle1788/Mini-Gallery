from django import forms
from .models import UserImage, Colour, Colour_Priority
from CommunityInfrastructure.models import City
from django.forms.widgets import TextInput
from django_select2 import forms as s2forms
from django_select2.forms import Select2Widget,Select2MultipleWidget



class ColourForm(forms.ModelForm):
    class Meta:
        model=Colour
        fields='__all__'



class ColourPriorityForm(forms.ModelForm):
    class Meta:
        model=Colour_Priority
        fields='__all__'


# class City_Form(forms.ModelForm):
#     class Meta:
#         model=City
#         fields=['region','city_name']
#         widgets={
#         'region':forms.Select(attrs={'class':'form-control apply_select2'})
#         }

# class FilterImages(forms.ModelForm):
#
#     class Meta:
#         model=UserImage
#         # fields=['system']
#         fields=['system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','paintingstudio','owner','location']
#         widgets={
#         'system':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'faction_type':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'factions':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'sub_factions':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'colours':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'conversion':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         # 'unit_type':forms.CheckboxSelectMultiple(attrs={'class':'form-control js-example-basic-single'}),
#         'unit_type':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'scale':forms.Select(attrs={'class':'form-control apply_select2'}),
#         'paintingstudio':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'owner':forms.TextInput(attrs={'class':'form-control','placeholder':'Name or Identifier'}),
#         'location':forms.SelectMultiple(attrs={'class':'form-control apply_select2'})
#         }
#




class UploadImages(forms.ModelForm):

    class Meta:
        model=UserImage
        fields=['image','image_title','system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','paintingstudio','owner','location']
        widgets={
        'system':Select2MultipleWidget,
        'faction_type':Select2MultipleWidget,
        'factions':Select2MultipleWidget,
        'sub_factions':Select2MultipleWidget,
        'colours':Select2MultipleWidget,
        'conversion':Select2MultipleWidget,
        'unit_type':Select2MultipleWidget,
        'scale':Select2Widget,
        'paintingstudio':Select2MultipleWidget,
        'owner':forms.TextInput({'placeholder':'Name or Identifier'}),#fix this
        'location':Select2Widget
        }

class UploadMultipleImages(forms.ModelForm):
    image= forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model=UserImage
        fields=['image','image_title','system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','paintingstudio','owner','location']
        widgets={
        # 'image':forms.ClearableFileInput(),
        # 'image':forms.ClearableFileInput(attrs={'multiple': True}),
        'system':Select2MultipleWidget,
        'faction_type':Select2MultipleWidget,
        'factions':Select2MultipleWidget,
        'sub_factions':Select2MultipleWidget,
        'colours':Select2MultipleWidget,
        'conversion':Select2MultipleWidget,
        'unit_type':Select2MultipleWidget,
        'scale':Select2Widget,
        'paintingstudio':Select2MultipleWidget,
        'owner':forms.TextInput({'placeholder':'Name or Identifier'}),#fix this
        'location':Select2Widget
        }

#
# file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))








#
#
# class UploadImages(forms.ModelForm):
#
#     class Meta:
#         model=UserImage
#         fields=['image','image_title','system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','paintingstudio','owner','location']
#         widgets={
#         'system':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'faction_type':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'factions':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'sub_factions':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'colours':forms.SelectMultiple(attrs={'class':'form-control apply_select2','id':'upload_id_colours'}),
#         'conversion':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         # ,'required':'True'
#         # 'unit_type':forms.CheckboxSelectMultiple(attrs={'class':'form-control js-example-basic-single'}),
#         'unit_type':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'scale':forms.Select(attrs={'class':'form-control apply_select2'}),
#         'paintingstudio':forms.SelectMultiple(attrs={'class':'form-control apply_select2'}),
#         'owner':forms.TextInput(attrs={'class':'form-control','placeholder':'FirstName LastName'}),
#         'location':forms.SelectMultiple(attrs={'class':'form-control apply_select2'})
#         }

# it sounds like we can use ajax to send requests to the server which would make the pruning easier b/c we could just ask the server directly for the connection and it can return the final value


# onChange="javascript:doSomething();

# {'onchange' : "myFunction(this.value);"}
#
# myFunction(value) {
#     console.log(value)
# }

#
#
#
#
# Text inputs
#         TextInput
#         NumberInput  (this one has a don't use me disclaimer)
#         EmailInput
#         URLInput
#         PasswordInput
#         HiddenInput
#         DateInput
#         DateTimeInput
#         TimeInput
#         Textarea
#
#
#
#
# Selector and checkbox widgets
#
#
#     CheckboxInput
#     Select
#     NullBooleanSelect
#     SelectMultiple
#     RadioSelect
#     CheckboxSelectMultiple
#
#
#
# Fiel Upload widgets
#
#
#
#     FileInput
#     ClearableFileInput
#
#
# Composite widgets
#
#
#     MultipleHiddenInput
#     SplitDateTimeWidget
#     SplitHiddenDateTimeWidget
#     SelectDateWidget
#
#
