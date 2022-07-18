from django.urls import path

from .views import *

urlpatterns = [

path('unit_type/add',Unit_Type_Create.as_view(),name='add unit type'),
path('system/add', System_Create.as_view(), name='add system'),
path('faction_type/add', Faction_Type_Create.as_view(), name='add faction type'),
path('faction/add', Faction_Create.as_view(), name='add faction'),
path('sub_faction/add', Sub_Faction_Create.as_view(), name='add sub faction'),

]
