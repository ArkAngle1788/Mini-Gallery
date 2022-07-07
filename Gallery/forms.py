from django import forms
from .models import UserImage, Colour, Colour_Priority
from CommunityInfrastructure.models import City
from django.forms.widgets import TextInput
from django_select2 import forms as s2forms
from django_select2.forms import Select2Widget,Select2MultipleWidget

basicattrs={'class':'bg-white'}

class ColourForm(forms.ModelForm):
    class Meta:
        model=Colour
        fields='__all__'
        widgets = {
            'colour_name': forms.TextInput(basicattrs),
        }


class ColourPriorityForm(forms.ModelForm):
    class Meta:
        model=Colour_Priority
        fields='__all__'
        widgets = {
            'colour_priority': forms.TextInput(basicattrs),
        }

# class City_Form(forms.ModelForm):
#     class Meta:
#         model=City
#         fields=['region','city_name']
#         widgets={
#         'region':forms.Select(attrs={'class':'form-control apply_select2'})
#         }



class UploadImages(forms.ModelForm):

    class Meta:
        model=UserImage
        fields=['image','image_title','system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','paintingstudio','owner','location']
        widgets={
        'image_title':forms.TextInput(attrs={'class': 'bg-white'}),
        'system':Select2MultipleWidget,
        'faction_type':Select2MultipleWidget,
        'factions':Select2MultipleWidget,
        'sub_factions':Select2MultipleWidget,
        'colours':Select2MultipleWidget,
        'conversion':Select2MultipleWidget,
        'unit_type':Select2MultipleWidget,
        'scale':Select2Widget,
        'paintingstudio':Select2MultipleWidget,
        'owner':forms.TextInput(attrs={'class': 'bg-white','placeholder':'Name or Identifier'}),
        'location':Select2Widget
        }
        # labels = {'system': 'Label 2'}

class UploadImagesMultipart(forms.ModelForm):
    subimage= forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True,'class':'text-text-sidebar'}),help_text="<---Select Multipule Subimages here!")
    class Meta:
        model=UserImage
        fields=['subimage','image_title','system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','paintingstudio','owner','location']
        widgets={
        'image_title':forms.TextInput(attrs={'class': 'bg-white'}),
        'system':Select2MultipleWidget,
        'faction_type':Select2MultipleWidget,
        'factions':Select2MultipleWidget,
        'sub_factions':Select2MultipleWidget,
        'colours':Select2MultipleWidget,
        'conversion':Select2MultipleWidget,
        'unit_type':Select2MultipleWidget,
        'scale':Select2Widget,
        'paintingstudio':Select2MultipleWidget,
        'owner':forms.TextInput(attrs={'class': 'bg-white','placeholder':'Name or Identifier'}),
        'location':Select2Widget
        }
        # help_texts = {
        #     'image': '<---Select Primary Display Image',
        # }

class SelectPrimaryImage(forms.Form):
    select_primary=forms.ChoiceField(choices=[],widget=forms.Select(basicattrs))
    def __init__(self, image_options=None, *args, **kwargs):
        super(SelectPrimaryImage, self).__init__(*args, **kwargs)
        if image_options:
            self.fields['select_primary'].choices = [
                (str(k), v)
                for k, v in enumerate(image_options)
            ]

class UploadMultipleImages(forms.ModelForm):
    image= forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model=UserImage
        fields=['image','image_title','system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','paintingstudio','owner','location']
        widgets={
        # 'image':forms.ClearableFileInput(),
        # 'image':forms.ClearableFileInput(attrs={'multiple': True}),
        'image_title':forms.TextInput(attrs={'class': 'bg-white'}),
        'system':Select2MultipleWidget,
        'faction_type':Select2MultipleWidget,
        'factions':Select2MultipleWidget,
        'sub_factions':Select2MultipleWidget,
        'colours':Select2MultipleWidget,
        'conversion':Select2MultipleWidget,
        'unit_type':Select2MultipleWidget,
        'scale':Select2Widget,
        'paintingstudio':Select2MultipleWidget,
        'owner':forms.TextInput({'class': 'bg-white','placeholder':'Name or Identifier'}),#fix this
        'location':Select2Widget
        }

#
# file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))



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
