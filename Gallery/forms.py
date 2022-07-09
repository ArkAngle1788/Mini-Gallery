from django import forms
from .models import UserImage, Colour, Colour_Priority,UserSubImage
from CommunityInfrastructure.models import City
from django.forms.widgets import TextInput,CheckboxSelectMultiple
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

from django.core.exceptions import ValidationError
from django.forms.fields import FileField




# class subChoiceField(forms.ChoiceField):
#     def to_python(self, value):
#
#         return super().to_python(value)
#     def run_validators(self, value):
#         print(f"-------custom run_validators: ")
#         if value in self.empty_values:
#             return
#         errors = []
#         for v in self.validators:
#             try:
#                 print(f"try print value:\n")
#                 print(v(value))
#             except ValidationError as e:
#                 if hasattr(e, "code") and e.code in self.error_messages:
#                     e.message = self.error_messages[e.code]
#                 errors.extend(e.error_list)
#         if errors:
#             raise ValidationError(errors)
#     def valid_value(self, value):
#         """Check to see if the provided value is a valid choice."""
#         text_value = str(value)
#         print(f"\n\nvalid value self.choices: {self.choices}\n\n")
#         for k, v in self.choices:
#             if isinstance(v, (list, tuple)):
#                 # This is an optgroup, so look inside the group for options
#                 for k2, v2 in v:
#                     print(f"value == {k2} or {text_value} == {str(k2)}")
#                     if value == k2 or text_value == str(k2):
#                         print(f"return true: {k2}")
#                         return True
#             else:
#                 print(f"else value == {k} or {text_value} == {str(k)}")
#                 if value == k or text_value == str(k):
#                     print(f"return true: {k}")
#                     return True
#         return False
#     def validate(self,value):
#         print('in validate---------\n')
#
#         super().validate(value)
#         if value and not self.valid_value(value):
#             raise ValidationError(
#                 self.error_messages["invalid_choice"],
#                 code="invalid_choice",
#                 params={"value": value},
#             )
class UpdateSubImages(forms.ModelForm):

    def __init__(self, parent_pk=None, *args, **kwargs):
        super(UpdateSubImages, self).__init__(*args, **kwargs)
        sub_images=[]
        for img in UserSubImage.objects.filter(parent_image__pk=parent_pk):
            sub_images.append([img.pk,img])
        self.fields['sub'].choices=sub_images


    image= forms.ImageField(label='Add Sub Images',required=False,widget=forms.ClearableFileInput(attrs={'multiple': True,'class':'text-text-sidebar'}),help_text="<---Select Subimages here!")
    sub = forms.ChoiceField(required=False,label='Delete Images',choices=[])

    class Meta:
        model=UserSubImage
        fields=['image','sub']
        # widgets={
        # 'image_title':forms.TextInput(attrs={'class': 'bg-white'}),
        # }


    def _clean_fields(self):
        for name, bf in self._bound_items():
            field = bf.field
            value = bf.initial if field.disabled else bf.data
            try:
                if isinstance(field, FileField):
                    for img in self.files.getlist("image"):
                        field.clean(img,bf.initial)
                    value = field.clean(value, bf.initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, "clean_%s" % name):
                    value = getattr(self, "clean_%s" % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                self.add_error(name, e)

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
    def _clean_fields(self):
        for name, bf in self._bound_items():
            field = bf.field
            value = bf.initial if field.disabled else bf.data
            try:
                if isinstance(field, FileField):
                    for img in self.files.getlist("subimage"):
                        field.clean(img,bf.initial)
                    value = field.clean(value, bf.initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, "clean_%s" % name):
                    value = getattr(self, "clean_%s" % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                self.add_error(name, e)

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

    def _clean_fields(self):
        for name, bf in self._bound_items():
            field = bf.field
            value = bf.initial if field.disabled else bf.data
            try:
                if isinstance(field, FileField):
                    for img in self.files.getlist("image"):
                        field.clean(img,bf.initial)
                    value = field.clean(value, bf.initial)
                else:
                    value = field.clean(value)
                self.cleaned_data[name] = value
                if hasattr(self, "clean_%s" % name):
                    value = getattr(self, "clean_%s" % name)()
                    self.cleaned_data[name] = value
            except ValidationError as e:
                self.add_error(name, e)

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
