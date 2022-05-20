from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from .models import *
from .forms import *

class Unit_Type_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Unit_Type
    # fields='__all__'
    form_class = Unit_TypeForm
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_unit_type')

class System_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Games
    # fields='__all__'
    form_class = SystemForm
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_system')

class Faction_Type_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Faction_Type
    # fields='__all__'
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_faction_type')
    form_class = Faction_TypeForm
    # success_url = "/"

class Faction_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Faction
    # fields='__all__'
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_faction')
    form_class = FactionForm
    # success_url = "/"

class Sub_Faction_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Sub_Faction
    # fields='__all__'
    form_class = Sub_FactionForm
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_sub_faction')
