import django_filters
from django_filters import CharFilter,ModelChoiceFilter,ModelMultipleChoiceFilter

from .models import UserImage, Colour, Colour_Catagory,Conversion,Scale_Of_Image
from CommunityInfrastructure.models import City,PaintingStudio
from GameData.models import Games,Faction_Type,Faction,Sub_Faction,Unit_Type

from django_select2.forms import Select2Widget,Select2MultipleWidget
from django.forms.widgets import TextInput
from django.db.models import Count #used for sorting likes
from django.forms import RadioSelect

global_default={'style':'width: 100%'}


#
# CHOICES=[('select1','select 1'),
#          ('select2','select 2')]
#
# like = forms.ChoiceField(choices=CHOICES, widget=forms.RadioSelect)

class CustomOrderingFilter(django_filters.OrderingFilter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra['choices'] += [
            ('popularity', 'Popularity'),
            ('recent', 'Recently Uploaded'),
        ]
        # self.extra['required']=True
        # for field_name in self.fields:
        #     field = self.fields.get(field_name)
        #     if field and isinstance(field , forms.TypedChoiceField):
        #         field.choices = field.choices[1:]


    def filter(self, qs, value):

        if value:

            # OrderingFilter is CSV-based, so `value` is a list
            # if any(v in ['popularity'] for v in value):
            #
            #     # sort queryset by relevance
            #     qs=qs.annotate(num_likes=Count('popularity')).order_by('-num_likes')
            #     # for var in qs:
            #     #     print(var.id)
            #     return qs

            if value[0]=='popularity':
                qs=qs.annotate(num_likes=Count('popularity')).order_by('-num_likes','id')

                return qs
            if value[0]=='recent':
                return qs.order_by('-pk')

        return super().filter(qs, value)

class ImageFilter(django_filters.FilterSet):#conjoined=True allows us to do an AND multipule item search instead of an OR



    fuzzy_search=CharFilter(label='Keyword Search',field_name="fuzzy_tags",lookup_expr='icontains',widget=TextInput({'style':'width: 100%','placeholder':'keyword search'}))
    title=CharFilter(label='Image Title',field_name="image_title",lookup_expr='icontains',widget=TextInput({'style':'width: 100%','placeholder':'Image Title'}))
    system=ModelMultipleChoiceFilter(queryset=Games.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    faction_type=ModelMultipleChoiceFilter(queryset=Faction_Type.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    factions=ModelMultipleChoiceFilter(queryset=Faction.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    sub_factions=ModelMultipleChoiceFilter(queryset=Sub_Faction.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    colours=ModelMultipleChoiceFilter(queryset=Colour_Catagory.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    conversion=ModelMultipleChoiceFilter(queryset=Conversion.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    unit_type=ModelMultipleChoiceFilter(queryset=Unit_Type.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    scale=ModelChoiceFilter(queryset=Scale_Of_Image.objects.all(),widget=Select2Widget(global_default))
    paintingstudio=ModelMultipleChoiceFilter(queryset=PaintingStudio.objects.all(),conjoined=True,widget=Select2MultipleWidget(global_default))
    owner=CharFilter(label='Owner',field_name='owner',lookup_expr='icontains',widget=TextInput({'style':'width: 100%','placeholder':'Name or Identifier'}))
    location=ModelChoiceFilter(queryset=City.objects.all(),widget=Select2Widget(global_default))

    order = CustomOrderingFilter(
        # initial='popularity',
        label='Sorty By',
        empty_label=None,
        widget=RadioSelect
        # fields=(
        #     ('id', 'idtest'),
        #
        #     ),
        #     field_labels={
        #         'id': 'Recently Uploaded',
        #     }
    )

    class Meta:
        model = UserImage
        fields = ['order','fuzzy_search','title','system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','paintingstudio','owner','location']
