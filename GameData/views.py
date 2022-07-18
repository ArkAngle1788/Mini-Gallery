from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import CreateView
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from .models import *
from .forms import *

class Unit_Type_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Unit_Type
    form_class = Unit_TypeForm
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_unit_type')

class System_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Games
    form_class = SystemForm
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_system')

class Faction_Type_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Faction_Type
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_faction_type')
    form_class = Faction_TypeForm

class Faction_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Faction
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_faction')
    form_class = FactionForm

class Sub_Faction_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Sub_Faction
    form_class = Sub_FactionForm
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_sub_faction')
