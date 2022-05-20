import django_filters
from django_filters import CharFilter,ModelChoiceFilter,ModelMultipleChoiceFilter

from .models import UserImage, Colour, Colour_Catagory,Conversion,Scale_Of_Image
from CommunityInfrastructure.models import City,PaintingStudio
from GameData.models import Games,Faction_Type,Faction,Sub_Faction,Unit_Type

from django_select2.forms import Select2Widget,Select2MultipleWidget
from django.forms.widgets import TextInput

global_default={'style':'width: 100%'}


class ImageFilter(django_filters.FilterSet):#conjoined=True allows us to do an AND multipule item search instead of an OR
    title=CharFilter(field_name="image_title",lookup_expr='icontains',widget=TextInput({'style':'width: 100%','placeholder':'Image Title'}))
    system=ModelMultipleChoiceFilter(queryset=Games.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    faction_type=ModelMultipleChoiceFilter(queryset=Faction_Type.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    factions=ModelMultipleChoiceFilter(queryset=Faction.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    sub_factions=ModelMultipleChoiceFilter(queryset=Sub_Faction.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    colours=ModelMultipleChoiceFilter(queryset=Colour_Catagory.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    conversion=ModelMultipleChoiceFilter(queryset=Conversion.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    unit_type=ModelMultipleChoiceFilter(queryset=Unit_Type.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    scale=ModelChoiceFilter(queryset=Scale_Of_Image.objects.all(),widget=Select2Widget(global_default))
    paintingstudio=ModelMultipleChoiceFilter(queryset=PaintingStudio.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    owner=CharFilter(field_name='owner',lookup_expr='icontains',widget=TextInput({'style':'width: 100%','placeholder':'Name or Identifier'}))
    location=ModelChoiceFilter(queryset=City.objects.all(),widget=Select2Widget(global_default))

    class Meta:
        model = UserImage
        fields = ['title','system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','paintingstudio','owner','location']
