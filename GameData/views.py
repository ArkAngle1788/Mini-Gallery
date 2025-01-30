from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin, UserPassesTestMixin)
from django.views.generic import DeleteView, UpdateView
from django.views.generic.edit import CreateView
from Gallery.filters import ImageFilter
from Gallery.models import UserImage

from .forms import (FactionForm, FactionTypeForm, SubFactionForm, SystemForm,
                    UnitTypeForm,ArmyListForm)
from .models import Faction, FactionType, Game, SubFaction, UnitType, ArmyList
from League.models import PlayerSeasonFaction
from UserAccounts.models import AdminProfile, UserProfile
from django.urls import reverse, reverse_lazy

class UnitTypeCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """requires add_unit_type permission"""
    model = UnitType
    form_class = UnitTypeForm
    template_name = 'GameData/game_data_form.html'
    permission_required = ('GameData.add_unit_type')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        # context['news'] = calculate_news_bar()
        image_filter = ImageFilter(
            self.request.GET, queryset=UserImage.objects.all())
        context['filter_form'] = image_filter
        return context


class SystemCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """requires add_system permission"""
    model = Game
    form_class = SystemForm
    template_name = 'GameData/game_data_form.html'
    permission_required = ('GameData.add_system')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        # context['news'] = calculate_news_bar()
        image_filter = ImageFilter(
            self.request.GET, queryset=UserImage.objects.all())
        context['filter_form'] = image_filter
        return context


class FactionTypeCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """requires add_faction_type permission"""
    model = FactionType
    template_name = 'GameData/game_data_form.html'
    permission_required = ('GameData.add_faction_type')
    form_class = FactionTypeForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        # context['news'] = calculate_news_bar()
        image_filter = ImageFilter(
            self.request.GET, queryset=UserImage.objects.all())
        context['filter_form'] = image_filter
        return context


class FactionCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """requires add_faction permission"""
    model = Faction
    template_name = 'GameData/game_data_form.html'
    permission_required = ('GameData.add_faction')
    form_class = FactionForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        # context['news'] = calculate_news_bar()
        image_filter = ImageFilter(
            self.request.GET, queryset=UserImage.objects.all())
        context['filter_form'] = image_filter
        return context


class SubFactionCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """requires add_sub_faction permission"""
    model = SubFaction
    form_class = SubFactionForm
    template_name = 'GameData/game_data_form.html'
    permission_required = ('GameData.add_sub_faction')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        # context['news'] = calculate_news_bar()
        image_filter = ImageFilter(
            self.request.GET, queryset=UserImage.objects.all())
        context['filter_form'] = image_filter
        return context


class ArmyListCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """requires staff status"""
    model = ArmyList
    form_class = ArmyListForm
    # permission_required = ("staff")

    def form_valid(self, form):
        # psf id is in the url so we set it based off that
        psf = PlayerSeasonFaction.objects.get(pk=self.kwargs['psfpk'])
        if self.request.user.profile != psf.profile:
            if not self.test_func():
                return self.form_invalid(form)
        form.instance.psf = psf
        valid_object = super().form_valid(form)
        return valid_object
    

    def get_success_url(self):
        return reverse('psf view', kwargs={'pk': self.kwargs['psfpk']})
    
    def test_func(self):
        """must manage league or be the psf in question to access"""

        if self.request.user.is_staff:
            return True

        if AdminProfile.objects.filter(userprofile__user=self.request.user):
            
            if (
                    self.get_object().season.league
                    in
                    self.request.user.profile.linked_admin_profile.leagues_managed.all()):
                return True
        if self.request.user == UserProfile.objects.get(pk=self.kwargs['psfpk']).user:
            return True

        return False


class ArmyListDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """requires staff status"""
    model = ArmyList
    # success_url = reverse_lazy('profile self')
    def get_success_url(self):
        return reverse('psf view', kwargs={'pk': self.kwargs['psfpk']})
    def test_func(self):
        """must manage league or be the psf in question to access"""

        if self.request.user.is_staff:
            return True

        if AdminProfile.objects.filter(userprofile__user=self.request.user):
            
            if (
                    self.get_object().season.league
                    in
                    self.request.user.profile.linked_admin_profile.leagues_managed.all()):
                return True
        if self.request.user == UserProfile.objects.get(pk=self.kwargs['psfpk']).user:
            return True

        return False


class ArmyListEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """you can only edit your own list"""
    model = ArmyList
    form_class = ArmyListForm
    def get_success_url(self):
        return reverse('psf view', kwargs={'pk': self.kwargs['psfpk']})
    def form_valid(self, form):
        # psf id is in the url so we set it based off that
        psf = PlayerSeasonFaction.objects.get(pk=self.kwargs['psfpk'])
        if self.request.user.profile != psf.profile:
            if not self.test_func():
                return self.form_invalid(form)
        form.instance.psf = psf
        valid_object = super().form_valid(form)
        return valid_object

    def test_func(self):
        """must manage league or be the psf in question to access"""

        if self.request.user.is_staff:
            return True

        if AdminProfile.objects.filter(userprofile__user=self.request.user):
            
            if (
                    self.get_object().season.league
                    in
                    self.request.user.profile.linked_admin_profile.leagues_managed.all()):
                return True
        if self.request.user == UserProfile.objects.get(pk=self.kwargs['psfpk']).user:
            return True

        return False