import django_filters
from django.db.models import Count  # used for sorting likes
from django.forms import RadioSelect
from django.forms.widgets import CheckboxInput, TextInput
from django_filters import (CharFilter, ModelChoiceFilter,
                            ModelMultipleChoiceFilter)
from django_select2.forms import Select2MultipleWidget, Select2Widget

from CommunityInfrastructure.models import City, PaintingStudio
from GameData.models import Faction, FactionType, Game, SubFaction, UnitType
from League.models import Season

from .models import ColourCatagory, Conversion, ScaleOfImage, UserImage

global_default = {'style': 'width: 100%'}

# override the ordering filter to create the two types
# of orderings that are relevant to our use case


class CustomOrderingFilter(django_filters.OrderingFilter):
    """custom filtering that sorts by popularity and recent uploads"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.extra['choices'] += [
            ('popularity', 'Popularity'),
            ('recent', 'Recently Uploaded'),
        ]

    def filter(self, qs, value):

        if value:
            # OrderingFilter is CSV-based, so `value` is a list
            if value[0] == 'popularity':
                qs = qs.annotate(num_likes=Count('popularity')
                                 ).order_by('-num_likes', 'id')
                return qs
            if value[0] == 'recent':
                return qs.order_by('-pk')

        return super().filter(qs, value)


class OfficialStudioFilter(django_filters.BooleanFilter):
    """
    Because StudioImages is not defined for images that are not associated
    with a painting studio we exclude all null entries to find the set of studio images

    We override the filterclass because we need to take no action of filter
    input is false and we also still need to only display official images if true.
    """

    def filter(self, qs, value):
        if value:  # value is the filter input the user selects
            # if value is true we want only the official images and the queryset
            # starts as UserImages that have any paintingstudio tags not official ones specifically
            qs = qs.filter(studioimages__official=True)
            return super().filter(qs, value)
        # if value was false we do not want to change the queryset in any way so we just return it
        return qs



class ImageFilter(django_filters.FilterSet):
    """
    conjoined=True allows us to do an AND multipule item search instead of an OR
    """

    fuzzy_search = CharFilter(
        label='Keyword Search', field_name="fuzzy_tags", lookup_expr='icontains',
        widget=TextInput({'style': 'width: 100%',
                          'placeholder': 'keyword search'}))
    title = CharFilter(label='Image Title', field_name="image_title", lookup_expr='icontains',
                       widget=TextInput({'style': 'width: 100%', 'placeholder': 'Image Title'}))
    system = ModelMultipleChoiceFilter(queryset=Game.objects.all(
    ), conjoined=True, widget=Select2MultipleWidget(global_default))
    faction_type = ModelMultipleChoiceFilter(queryset=FactionType.objects.all(
    ), conjoined=True, widget=Select2MultipleWidget(global_default))
    factions = ModelMultipleChoiceFilter(queryset=Faction.objects.all(
    ), conjoined=True, widget=Select2MultipleWidget(global_default))
    sub_factions = ModelMultipleChoiceFilter(queryset=SubFaction.objects.all(
    ), conjoined=True, widget=Select2MultipleWidget(global_default))
    source = ModelMultipleChoiceFilter(
        queryset=Season.objects.all(), widget=Select2MultipleWidget(global_default))
    colours = ModelMultipleChoiceFilter(queryset=ColourCatagory.objects.all(
    ), conjoined=True, widget=Select2MultipleWidget(global_default))
    conversion = ModelMultipleChoiceFilter(queryset=Conversion.objects.all(
    ), conjoined=True, widget=Select2MultipleWidget(global_default))
    unit_type = ModelMultipleChoiceFilter(queryset=UnitType.objects.all(
    ), conjoined=True, widget=Select2MultipleWidget(global_default))
    scale = ModelChoiceFilter(
        queryset=ScaleOfImage.objects.all(), widget=Select2Widget(global_default))
    paintingstudio = ModelMultipleChoiceFilter(queryset=PaintingStudio.objects.all(
    ), conjoined=True, widget=Select2MultipleWidget(global_default))
    owner = CharFilter(label='Owner', field_name='owner', lookup_expr='icontains', widget=TextInput(
        {'style': 'width: 100%', 'placeholder': 'Name or Identifier'}))
    location = ModelChoiceFilter(
        queryset=City.objects.all(), widget=Select2Widget(global_default))

    order = CustomOrderingFilter(
        # initial='popularity',
        label='Sort By',
        empty_label=None,
        widget=RadioSelect
    )

    studio_official = OfficialStudioFilter(

        label='Show only official studio uploads',
        field_name='paintingstudio',
        lookup_expr='studioimages__official__isnull',
        exclude=True,
        widget=CheckboxInput

    )

    class Meta:
        model = UserImage
        fields = [
            'order', 'fuzzy_search', 'title', 'system', 'faction_type',
            'factions', 'sub_factions', 'source' ,'colours', 'conversion',
            'unit_type', 'scale', 'studio_official', 'paintingstudio', 'owner', 'location']
