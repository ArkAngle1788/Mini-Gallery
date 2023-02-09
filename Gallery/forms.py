from django import forms
from django.core.exceptions import ValidationError
from django.forms.fields import FileField
from django_select2.forms import Select2MultipleWidget, Select2Widget

from .models import Colour, ColourPriority, UserImage, UserSubImage

basicattrs = {'class': 'bg-white'}


class ColourForm(forms.ModelForm):
    """colour is used to build colour catagory"""
    class Meta:
        model = Colour
        fields = '__all__'
        widgets = {
            'colour_name': forms.TextInput(basicattrs),
        }


class ColourPriorityForm(forms.ModelForm):
    """priority is used to build colour catagory"""
    class Meta:
        model = ColourPriority
        fields = '__all__'
        widgets = {
            'colour_priority': forms.TextInput(basicattrs),
        }


class UploadImages(forms.ModelForm):
    """Upload a single image"""

    class Meta:
        model = UserImage
        fields = ['image', 'image_title', 'system',
                  'faction_type', 'factions', 'sub_factions',
                  'source','colours', 'conversion', 'unit_type',
                  'scale', 'paintingstudio', 'owner', 'location']
        widgets = {
            'image_title': forms.TextInput(attrs={'class': 'bg-white'}),
            'system': Select2MultipleWidget,
            'faction_type': Select2MultipleWidget,
            'factions': Select2MultipleWidget,
            'sub_factions': Select2MultipleWidget,
            'source': Select2Widget,
            'colours': Select2MultipleWidget,
            'conversion': Select2MultipleWidget,
            'unit_type': Select2MultipleWidget,
            'scale': Select2Widget,
            'paintingstudio': Select2MultipleWidget,
            'owner': forms.TextInput(
                attrs={'class': 'bg-white', 'placeholder': 'Name or Identifier'}),
            'location': Select2Widget
        }


class UpdateSubImages(forms.ModelForm):
    """allows the subgallery images for a UserImage to be updated"""

    def __init__(self,  *args, parent_pk=None, **kwargs):
        super(UpdateSubImages, self).__init__(*args, **kwargs)
        sub_images = []
        for img in UserSubImage.objects.filter(parent_image__pk=parent_pk):
            sub_images.append([img.pk, img])
        self.fields['sub'].choices = sub_images

    image = forms.ImageField(label='Add Sub Images',
                             required=False, widget=forms.ClearableFileInput(
                                 attrs={'multiple': True, 'class': 'text-text-sidebar'}),
                             help_text="<---Select Subimages here!")
    sub = forms.ChoiceField(required=False, label='Delete Images', choices=[])

    class Meta:
        model = UserSubImage
        fields = ['image', 'sub']

    def _clean_fields(self):
        for name, bf in self._bound_items():
            field = bf.field
            value = bf.initial if field.disabled else bf.data
            try:
                if isinstance(field, FileField):
                    for img in self.files.getlist("image"):
                        field.clean(img, bf.initial)
                    value = field.clean(value, bf.initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, "clean_%s" % name):
                    value = getattr(self, "clean_%s" % name)()
                    self.cleaned_data[name] = value
            except ValidationError as error:
                self.add_error(name, error)


class UploadImagesMultipart(forms.ModelForm):
    """upload a set of images that share one entry"""
    subimage = forms.ImageField(widget=forms.ClearableFileInput(
        attrs={'multiple': True, 'class': 'text-text-sidebar'}),
        help_text="<---Select Multipule Subimages here!")

    class Meta:
        model = UserImage
        fields = ['subimage', 'image_title', 'system',
                  'faction_type', 'factions', 'sub_factions',
                  'source','colours', 'conversion', 'unit_type', 'scale',
                  'paintingstudio', 'owner', 'location']
        widgets = {
            'image_title': forms.TextInput(attrs={'class': 'bg-white'}),
            'system': Select2MultipleWidget,
            'faction_type': Select2MultipleWidget,
            'factions': Select2MultipleWidget,
            'sub_factions': Select2MultipleWidget,
            'source': Select2Widget,
            'colours': Select2MultipleWidget,
            'conversion': Select2MultipleWidget,
            'unit_type': Select2MultipleWidget,
            'scale': Select2Widget,
            'paintingstudio': Select2MultipleWidget,
            'owner': forms.TextInput(attrs={'class': 'bg-white',
                                            'placeholder': 'Name or Identifier'}),
            'location': Select2Widget
        }

    def _clean_fields(self):
        for name, bf in self._bound_items():
            field = bf.field
            value = bf.initial if field.disabled else bf.data
            try:
                if isinstance(field, FileField):
                    for img in self.files.getlist("subimage"):
                        field.clean(img, bf.initial)
                    value = field.clean(value, bf.initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, "clean_%s" % name):
                    value = getattr(self, "clean_%s" % name)()
                    self.cleaned_data[name] = value
            except ValidationError as error:
                self.add_error(name, error)


class SelectPrimaryImage(forms.Form):
    """init defines select_primary choice values"""
    select_primary = forms.ChoiceField(
        choices=[], widget=forms.Select(basicattrs))

    def __init__(self,  *args, image_options=None, **kwargs):
        super(SelectPrimaryImage, self).__init__(*args, **kwargs)
        if image_options:
            self.fields['select_primary'].choices = [
                (str(k), v)
                for k, v in enumerate(image_options)
            ]


class UploadMultipleImages(forms.ModelForm):
    """
    For multipule single image uploads
    form validates each image in the multiple upload
    """
    image = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}))

    class Meta:
        model = UserImage
        fields = ['image', 'image_title', 'system', 'faction_type', 'factions', 'sub_factions',
                  'source','colours', 'conversion', 'unit_type', 'scale',
                  'paintingstudio', 'owner', 'location']
        widgets = {
            'image_title': forms.TextInput(attrs={'class': 'bg-white'}),
            'system': Select2MultipleWidget,
            'faction_type': Select2MultipleWidget,
            'factions': Select2MultipleWidget,
            'sub_factions': Select2MultipleWidget,
            'source': Select2Widget,
            'colours': Select2MultipleWidget,
            'conversion': Select2MultipleWidget,
            'unit_type': Select2MultipleWidget,
            'scale': Select2Widget,
            'paintingstudio': Select2MultipleWidget,
            # fix this
            'owner': forms.TextInput({'class': 'bg-white', 'placeholder': 'Name or Identifier'}),
            'location': Select2Widget
        }

    def _clean_fields(self):
        for name, bf in self._bound_items():
            field = bf.field
            value = bf.initial if field.disabled else bf.data
            try:
                if isinstance(field, FileField):
                    for img in self.files.getlist("image"):
                        field.clean(img, bf.initial)
                    value = field.clean(value, bf.initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, "clean_%s" % name):
                    value = getattr(self, "clean_%s" % name)()
                    self.cleaned_data[name] = value
            except ValidationError as error:
                self.add_error(name, error)
