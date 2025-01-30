from django.urls import path

from .views import (FactionCreate, FactionTypeCreate, SubFactionCreate,
                    SystemCreate, UnitTypeCreate, ArmyListCreate, ArmyListEdit,ArmyListDelete)

urlpatterns = [

path('unit_type/add',UnitTypeCreate.as_view(),name='add unit type'),
path('system/add', SystemCreate.as_view(), name='add system'),
path('faction_type/add', FactionTypeCreate.as_view(), name='add faction type'),
path('faction/add', FactionCreate.as_view(), name='add faction'),
path('sub_faction/add', SubFactionCreate.as_view(), name='add sub faction'),
path('armylist/<int:psfpk>/create',ArmyListCreate.as_view(),name='create army list'),
path('armylist/<int:psfpk>/<int:pk>/edit', ArmyListEdit.as_view(), name='edit army list'),
path('armylist/<int:psfpk>/<int:pk>/delete', ArmyListDelete.as_view(), name='delete army list'),
]
