# from UserAccounts.models import UserProfile
# from Gallery.models import Professional
# from ContentPost.models import ContentPost
# from django.contrib.auth.decorators import login_required
# from itertools import count
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import (ImproperlyConfigured, ObjectDoesNotExist,
                                    ValidationError)
from django.http import Http404
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.urls import reverse
# from django.urls import reverse_lazy
# from .custom_functions import *
# from django.db.models import Q
# from django.http import HttpResponseNotFound
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from CommunityInfrastructure.models import Group
from Gallery.models import UserImage
from UserAccounts.models import UserProfile

from .forms import (LeagueForm, MatchEditForm, MatchForm, RoundForm,
                    SeasonForm, SeasonRegisterForm)
# from django.http import HttpResponseRedirect
# from GameData.models import Games, Faction, Faction_Type, Sub_Faction
from .models import League, Match, PlayerSeasonFaction, Round, Season


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

    def test_func(self):

        try:
            owning_group = Group.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff or (
            self.request.user.profile.linked_admin_profile
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
            (self.request.user.profile.linked_admin_profile
             in league.group.group_primary_admins.all())
            or
            (league in self.request.user.profile.leagues_managed.all())
        ):
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
        """must manage league to access"""
        try:
            parent_league = League.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if parent_league in self.request.user.profile.leagues_managed.all():
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
        """must manage league to access"""
        try:
            season = Season.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if season.league in self.request.user.profile.leagues_managed.all():
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

        key = form.cleaned_data['registration_key']
        season = Season.objects.get(pk=self.kwargs['pk'])
        if key != season.registration_key:
            form.add_error('registration_key', ValidationError(
                ('Invalid value'), code='invalid'))
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


class RoundCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """
    fields support markdown
    locks in the previous rounds w:l record string
    """
    model = Round
    form_class = RoundForm

    def test_func(self):
        """must manage league or be staff to access"""
        try:
            season = Season.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff:
            return True

        if season.league in self.request.user.profile.linked_admin_profile.leagues_managed.all():
            return True
        return False

    def get(self, request, *args, **kwargs):
        """ensures you have closed registration before making new rounds"""

        season = Season.objects.get(pk=self.kwargs['pk'])

        if season.registration_active:
            messages.error(
                self.request,
                'Creating a round can only be done when registration is closed.')

            url = reverse('season details', args=[self.kwargs['pk'],slugify(Season.objects.get(pk=self.kwargs['pk']).league)])
            return redirect(url)

        return super().get(self,request,*args,**kwargs)

    def post(self, request, *args, **kwargs):
        """ensures you have closed registration before making new rounds"""

        season = Season.objects.get(pk=self.kwargs['pk'])

        if season.registration_active:
            messages.error(
                self.request,
                'Creating a round can only be done when registration is closed.')

            url = reverse('season details', args=[self.kwargs['pk'],slugify(Season.objects.get(pk=self.kwargs['pk']).league)])
            return redirect(url)

        return super().post(self,request,*args,**kwargs)

    def form_valid(self, form):
        # group_id cannot be null so we must add it to the form info

        season = Season.objects.get(pk=self.kwargs['pk'])

        if form.cleaned_data['automate_matchmaking']:
            if season.seasons_rounds.all():
                if (season.seasons_rounds.order_by('pk').last().round_number
                    >=
                        (season.players_in_season.count()-1)):
                    messages.error(
                        self.request,
                        'Automatic Matchmaking Does not support this many rounds. \
                            Rematches Will Occur.')
                    return super().form_invalid(form)

        form.instance.season = season
        # check if this is the first round being created
        if season.seasons_rounds.all():
            # if rounds exist we also need to lock in the results of previous rounds

            for match in season.seasons_rounds.last().round_matches.all():
                match.player1.previous_opponents.add(match.player2)
                match.player1.score+=match.player1_score
                match.player1.matched=False

                match.player2.previous_opponents.add(match.player1)
                match.player2.score+=match.player2_score
                match.player2.matched=False
           
                if match.winner==match.player1:
                    match.player1.wlrecord+="W-" 
                    match.player2.wlrecord+="L-"
                else:
                    match.player1.wlrecord+="L-"
                    match.player2.wlrecord+="W-"

                match.player1.save()
                match.player2.save()

                    # NEED TO ADD TIE LOGIC
                    



            form.instance.round_number = season.seasons_rounds.count()+1

        else:
            form.instance.round_number = 1
            # also close registration?
        redirect_url = super().form_valid(form)

        if form.cleaned_data['automate_matchmaking']:
            # this will create matches when implemented
            print('automate matchmaking here!')

        return redirect_url


class RoundEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """only staff and the primary admins can edit."""
    model = Round
    form_class = RoundForm

    def test_func(self):
        """must manage league to access"""

        if (
                round.season.league
                in
                self.request.user.profile.linked_admin_profile.leagues_managed.all()):
            return True
        return False


class RoundView(DetailView):
    """Viewing rounds is public"""
    model = Round

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        # context['news']=calculate_news_bar()

        return context


class MatchCreateManual(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """comment"""
    model = Match
    form_class = MatchForm

    def test_func(self):
        """must manage league to access"""
        try:
            round_var = Round.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if (round_var.season.league
            in
                self.request.user.profile.linked_admin_profile.leagues_managed.all()):
            return True
        return False

    def form_valid(self, form):
        # group_id cannot be null so we must add it to the form info
        if form.cleaned_data['player1'] == form.cleaned_data['player2']:
            form.add_error('player2', ValidationError(
                ('A player cannot be matched against themselves'), code='invalid'))
            return super().form_invalid(form)

            # also check previously played

        round_var = Round.objects.get(pk=self.kwargs['pk'])
        form.instance.round = round_var

        return_url = super().form_valid(form)

        self.object.player1.matched = True
        self.object.player2.matched = True
        self.object.player1.save()
        self.object.player2.save()

        return return_url

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update({
            'season': Round.objects.get(pk=self.kwargs['pk']).season
        })
        return kwargs


class MatchEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    W:L record string is not generated until the round is closed
    """
    model = Match
    form_class = MatchEditForm

    def test_func(self):
        """must be one of the two players in a match during the round or a league admin"""
        try:
            match = Match.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff:
            return True

        if (match.round.season.league
            in
                self.request.user.profile.linked_admin_profile.leagues_managed.all()):
            return True

        # users in a match can edit results while the match is the most recent
        if match.player1 == self.request.user.profile.psf\
            or match.player2 == self.request.user.profile.psf:
            if match.round.season.seasons_rounds.last == match.round:
                return True
            messages.error(
                self.request,
                'You can only edit results for the current round. \
                    Contact and Admin if old results are invalid.')

        return False

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update({
            'player1': self.object.player1,
            'player2': self.object.player2
        })
        return kwargs


class MatchDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """only staff or primary admins can delete leagues"""
    model = Match

    def test_func(self):
        """must manage league to access"""
        try:
            match = Match.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if (match.round.season.league
            in
                self.request.user.profile.linked_admin_profile.leagues_managed.all()):
            return True
        return False

    def form_valid(self, form):

        self.object.player1.matched = False
        self.object.player2.matched = False
        self.object.player1.save()
        self.object.player2.save()

        return super().form_valid(form)

    def get_success_url(self):
        url = reverse('round details', args=[
                      self.object.round.id, slugify(self.object.round.season.league)])

        return url


class MatchView(DetailView):
    """Viewing Matches is public"""
    model = Match

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        # context['news']=calculate_news_bar()

        return context


class SubmitResults(LoginRequiredMixin, View):
    """
    shows active registerd leagues or
    redirects if there is only one
    """

    def get(self, request, *args, **kwargs):
        """expects no args"""

        matches = []

        for psf in self.request.user.profile.psf.all():
            if psf.season.season_active:
                last_round = psf.season.seasons_rounds.all().last()
                for match in last_round.round_matches.all():
                    if request.user.profile == match.player1.profile\
                        or request.user.profile == match.player2.profile:
                        matches += [match]

        if len(matches) == 1:
            url = reverse('edit match', args=[matches[0].id])

            return redirect(url)

        return render(request, 'League/submit_results.html',
                      {'matches': matches})
