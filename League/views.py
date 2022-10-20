# from UserAccounts.models import UserProfile
# from Gallery.models import Professional
# from ContentPost.models import ContentPost
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
# from django.contrib import messages
# from django.urls import reverse_lazy
# from .custom_functions import *
# from django.db.models import Q
# from django.http import HttpResponseNotFound
# from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.core.exceptions import ValidationError

from CommunityInfrastructure.models import Group
from Gallery.models import UserImage
from UserAccounts.models import UserProfile

from .forms import LeagueForm,SeasonForm,SeasonRegisterForm
# from django.http import HttpResponseRedirect
# from GameData.models import Games, Faction, Faction_Type, Sub_Faction
from .models import League,Season, PlayerSeasonFaction#, Round,Match


def leagues(request):
    """docstring"""

    image = UserProfile.objects.all()

    var = image.filter(id=200)
    print(var)

    var2 = UserImage.objects.all()[0]
    var2.paintingstudio.get(id=1)
    print(var2)
    print(var2.paintingstudio.get(id=1))

    print("fstring test")
    print(f"{var2}.model, {var2}.queryset, or override {var2}.get_queryset().")

    try:
        image.get(id=23)
    except ImproperlyConfigured:
        print('hi')
    except ObjectDoesNotExist as error:
        print('in except')
        print(error)
        # raise error
    else:
        print('try statement else')

    return render(request, 'CommunityInfrastructure/home.html')


class LeagueCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """can only be created by staff. fields support markdown"""
    model = League
    form_class = LeagueForm
    permission_required = ('staff')

    def test_func(self):

        try:
            owning_group = Group.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff or (
                self.request.user.profile.linked_admin_profile \
                    in owning_group.group_primary_admins.all()):
            return True
        return False

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update({
            'group': Group.objects.get(pk=self.kwargs['pk'])
        })
        return kwargs

    def form_valid(self, form):
        # group_id cannot be null so we must add it to the form info
        owning_group = Group.objects.get(pk=self.kwargs['pk'])
        form.instance.group = owning_group
        valid_object = super().form_valid(form)

        for admin in form.cleaned_data['admin_options']:
            admin.leagues_managed.add(self.object)
            admin.save()

        return valid_object


class LeagueEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """only staff and the primary admins can edit."""
    model = League
    form_class = LeagueForm

    def test_func(self):
        """only primary admins and staff can edit"""
        try:
            league = League.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff or (
            self.request.user.profile.linked_admin_profile
                in league.group_primary_admins.all()):
            return True
        return False

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update({
            'group': League.objects.get(pk=self.kwargs['pk']).group
        })
        return kwargs

    def form_valid(self, form):
        """group_id cannot be null so we must add it to the form info"""
        owning_group = League.objects.get(pk=self.kwargs['pk']).group
        form.instance.group = owning_group
        valid_object = super().form_valid(form)

        for admin in form.cleaned_data['admin_options']:
            admin.leagues_managed.add(self.object)
            admin.save()

        return valid_object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        context['group'] = self.object.group
        return context


class LeagueDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """only staff or primary admins can delete leagues"""
    model = League


    def test_func(self):
        """only primary admins and staff can delete"""
        try:
            league = League.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff or (
            self.request.user.profile.linked_admin_profile
                in league.group_primary_admins.all()):
            return True
        return False

    def get_success_url(self):
        url = reverse('group info', args=[
                      'region', self.object.group.slug(), self.object.group.id])

        return url


class LeagueView(DetailView):
    """Viewing leagues is public"""
    model = League


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        # context['news']=calculate_news_bar()
        context['reverse_seasons'] = self.object.child_season.all().order_by('-pk')
        return context

class SeasonCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """url param is the league the season belongs to"""
    model = Season
    form_class = SeasonForm

    def test_func(self):

        try:
            parent_league = League.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff or (
                self.request.user.profile.linked_admin_profile \
                    in parent_league.group.group_primary_admins.all()):
            return True
        return False


    def form_valid(self, form):
        # group_id cannot be null so we must add it to the form info
        parent_league = League.objects.get(pk=self.kwargs['pk'])
        form.instance.league = parent_league
        form.instance.season_active = False
        form.instance.registration_active = True

        return super().form_valid(form)


class SeasonEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """only staff and the primary admins can edit."""
    model = Season
    form_class = SeasonForm

    def test_func(self):
        """only primary admins and staff can edit"""
        try:
            season = Season.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff or (
            (self.request.user.profile.linked_admin_profile
            in season.league.group.group_primary_admins.all())
            or
            (self.request.user.profile.linked_admin_profile
            in season.league.group.group_secondary_admins.all())
            ):
            return True
        return False




class SeasonDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """only staff or primary admins can delete leagues"""
    model = Season


    def test_func(self):
        """only primary admins and staff can edit"""
        try:
            season = Season.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff or (
            (self.request.user.profile.linked_admin_profile
            in season.league.group.group_primary_admins.all())
            or
            (self.request.user.profile.linked_admin_profile
            in season.league.group.group_secondary_admins.all())
            ):
            return True
        return False

    def get_success_url(self):
        url = reverse('group info', args=[
                      'region', self.object.league.group.slug(), self.object.league.group.id])

        return url


class SeasonView(DetailView):
    """Viewing leagues is public"""
    model = Season


# for create round to be a valid call registration must be closed since createing a round will also create matchups.
# we can probably pass a parameter with the create round request that designates if we want to have manual or automatic matchmaking



class SeasonRegister(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """url param is the season to register for"""
    model = PlayerSeasonFaction
    form_class = SeasonRegisterForm

    def test_func(self):

        try:
            season = Season.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if not season.registration_active:
            return False

        return True


    def form_valid(self, form):
        # group_id cannot be null so we must add it to the form info

        key=form.cleaned_data['registration_key']
        season=Season.objects.get(pk=self.kwargs['pk'])
        if key!=season.registration_key:
            form.add_error('registration_key',ValidationError(('Invalid value'), code='invalid'))
            return super().form_invalid(form)

        form.instance.profile = self.request.user.profile
        form.instance.season = season

        return super().form_valid(form)

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update({
            'league': Season.objects.get(pk=self.kwargs['pk']).league
        })
        return kwargs
