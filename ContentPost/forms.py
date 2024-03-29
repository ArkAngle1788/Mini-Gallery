from django import forms
from markdownx.fields import MarkdownxFormField

from .models import ContentPost

# from django_select2 import forms as s2forms
# from django_select2.forms import Select2Widget,Select2MultipleWidget

basicattrs = {'class': 'bg-white'}


class ContentPostForm(forms.ModelForm):
    """text fields support markdown"""

    # markdownx is a bit of overkill but i'm leaving it here for now for future reference
    text1 = MarkdownxFormField()

    class Meta:
        model = ContentPost
        fields = ['headline', 'title', 'text1', 'image1', 'text2', 'image2',
                  'text3', 'image3', 'global_display', 'display_to_game', 'source']
        widgets = {
            'headline': forms.CheckboxInput(attrs={'class': ''}),
            # ,'style':'color:red'}),
            'title': forms.TextInput(attrs={'class': 'bg-white text-red'}),
            'text1': forms.TextInput(attrs={'class': 'bg-white'}),
            'text2': forms.TextInput(attrs={'class': 'bg-white'}),
            'text3': forms.TextInput(attrs={'class': 'bg-white'}),
            'global_display': forms.CheckboxInput(attrs={'class': ''}),
            'display_to_game': forms.SelectMultiple(attrs={'class': 'bg-white'}),
            'source': forms.Select(attrs={'class': 'bg-white'}),

        }
