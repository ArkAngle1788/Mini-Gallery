from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
# from django.views.generic import DeleteView, DetailView, ListView, UpdateView
from django.views.generic.edit import CreateView

from .forms import (FactionForm, FactionTypeForm, SubFactionForm, SystemForm,
                    UnitTypeForm)
from .models import Faction, FactionType, Game, SubFaction, UnitType


class UnitTypeCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    """requires add_unit_type permission"""
    model=UnitType
    form_class = UnitTypeForm
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_unit_type')

class SystemCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    """requires add_system permission"""
    model=Game
    form_class = SystemForm
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_system')

class FactionTypeCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    """requires add_faction_type permission"""
    model=FactionType
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_faction_type')
    form_class = FactionTypeForm

class FactionCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    """requires add_faction permission"""
    model=Faction
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_faction')
    form_class = FactionForm

class SubFactionCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    """requires add_sub_faction permission"""
    model=SubFaction
    form_class = SubFactionForm
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_sub_faction')
