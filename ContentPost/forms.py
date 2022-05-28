from django import forms
from .models import ContentPost

from django.forms.widgets import TextInput
from markdownx.fields import MarkdownxFormField
# from django_select2 import forms as s2forms
# from django_select2.forms import Select2Widget,Select2MultipleWidget

basicattrs={'class':'bg-white'}



class ContentPostForm(forms.ModelForm):

    # markdownx is a bit of overkill but i'm leaving it here for now for future reference
    text1 = MarkdownxFormField()

    class Meta:
        model=ContentPost
        fields=['headline','title','text1','image1','text2','image2','text3','image3','global_display','display_to_game','source']
        widgets={
        'headline':forms.CheckboxInput(attrs={'class': ''}),
        'title':forms.TextInput(attrs={'class': 'bg-white text-red'}),#,'style':'color:red'}),
        'text1':forms.TextInput(attrs={'class': 'bg-white'}),
        'text2':forms.TextInput(attrs={'class': 'bg-white'}),
        'text3':forms.TextInput(attrs={'class': 'bg-white'}),
        'global_display':forms.CheckboxInput(attrs={'class': ''}),
        'display_to_game':forms.SelectMultiple(attrs={'class': 'bg-white'}),
        'source':forms.Select(attrs={'class': 'bg-white'}),

        }


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
