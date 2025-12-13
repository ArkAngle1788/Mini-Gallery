
# from Gallery.models import Professional
# from ContentPost.models import ContentPost
# from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import (ImproperlyConfigured, ObjectDoesNotExist,
                                    ValidationError)
from django.db.models import Count  # used for sorting likes
from django.db.models import QuerySet, Q
from django.http import Http404
from django.shortcuts import redirect, render
from django.template.defaultfilters import slugify
from django.urls import reverse
# from django.http import HttpResponseNotFound
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_filters.views import FilterView
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from CommunityInfrastructure.custom_functions import (check_league_admin,
                                                      check_primary_admin)
from CommunityInfrastructure.models import Group
from Gallery.filters import ImageFilter
from Gallery.models import UserImage
from Gallery.views import GalleryMultipleUpload, GalleryUploadMultipart
from UserAccounts.models import AdminProfile, UserProfile

# from django.urls import reverse_lazy
from .custom_functions import auto_round_matches_basic, match_permission_check
from .forms import (LeagueForm, MatchEditForm, MatchForm,
                    MatchUploadMultipartImages, MatchUploadMultipleImages,
                    RoundForm, SeasonForm, SeasonRegisterForm,AddDropPlayerForm,
                    PSFUpdateForm)
# from django.http import HttpResponseRedirect
# from GameData.models import Games, Faction, Faction_Type, Sub_Faction
from .models import League, Match, PlayerSeasonFaction, Round, Season


def leagues(request):
    """this currently is some leftover debug fragment? why didn't I delete it when i finished whatever I was doing here?"""

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

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False
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

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False
        
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

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False
        
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

        if self.request.user.is_staff:
            return True

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False
    
        if parent_league in self.request.user.profile.linked_admin_profile.leagues_managed.all():
            return True
    
        return False

    def league_logic_test(self, request, *args, **kwargs):
        """
        tests if a new season is allowed to be created
        """

        league = League.objects.get(pk=self.kwargs['pk'])
        leagues_seasons = league.child_season.all()

        

        if leagues_seasons.count() > 1:

            # we can't check this on the first season and it's only relevant if there's more than 1.
            if leagues_seasons.last().registration_active:
                messages.error(
                    self.request,
                    'The previous season is still in registration.')
                return False

            iterate_var = 0
            for entry in leagues_seasons:
                if entry == leagues_seasons.last():
                    round_list = leagues_seasons[iterate_var -
                                                 1].seasons_rounds.all()
                    if round_list:
                        match_list = round_list.last().round_matches.all()
                        if match_list:
                            for match in match_list:
                                if not match.winner:
                                    messages.error(
                                        self.request,
                                        'There are unresolved matches in a previous season.')
                                    return False
                        else:
                            messages.error(
                                self.request,
                                'There is an unfinished round in a previous season.')
                            return False
                    else:
                        messages.error(
                            self.request,
                            'A previous season does not have any rounds')
                        return False
                iterate_var += 1
        return True

    def get(self, request, *args, **kwargs):
        """checks to make sure creating a new season is allowed"""

        if not self.league_logic_test(self, request, *args, **kwargs):
            url = reverse('league details', args=[self.kwargs['pk'], slugify(
                League.objects.get(pk=self.kwargs['pk']))])
            return redirect(url)

        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """checks to make sure creating a new season is allowed"""

        if not self.league_logic_test(self, request, *args, **kwargs):
            url = reverse('league details', args=[self.kwargs['pk'], slugify(
                League.objects.get(pk=self.kwargs['pk']))])
            return redirect(url)

        return super().post(self, request, *args, **kwargs)

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

        if self.request.user.is_staff:
            return True

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False

        if season.league in self.request.user.profile.linked_admin_profile.leagues_managed.all():
            return True
     
        return False


class SeasonClose(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    shows active registerd leagues or
    redirects if there is only one
    """

    def test_func(self):
        """must manage league to access"""
        try:
            season = Season.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff:
            return True

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False

        if season.league in self.request.user.profile.linked_admin_profile.leagues_managed.all():
            return True
        
        return False

    def season_logic_test(self, request, *args, **kwargs):
        """
        makes sure you are allowed to close the season
        """
        season = Season.objects.get(pk=self.kwargs['pk'])

        round_list = season.seasons_rounds.all()
        if round_list:
            match_list = round_list.last().round_matches.all()
            if match_list:
                for match in match_list:
                    if not match.winner:
                        messages.error(
                            self.request,
                            'There are unresolved matches in the season.')
                        return False
            else:
                messages.error(
                    self.request,
                    'There is an unfinished round in the season.')
                return False
        else:
            messages.error(
                self.request,
                'The season does not have any rounds')
            return False
        return True

    def get(self, request, *args, **kwargs):
        """expects no args"""
        # print("test")
        if not self.season_logic_test(self, request):
            url = reverse('season details', args=[self.kwargs['pk'], slugify(
                Season.objects.get(pk=self.kwargs['pk']).league)])
            return redirect(url)

        return render(request, 'League/close_season.html')

    def post(self, request, *args, **kwargs):
        """expects no args"""
        season = Season.objects.get(pk=self.kwargs['pk'])

        if not self.season_logic_test(self, request):
            url = reverse('season details', args=[self.kwargs['pk'], slugify(
                Season.objects.get(pk=self.kwargs['pk']).league)])
            return redirect(url)

        # in infinity bye round OP and VP are calculated at the end of the season
        if season.league.system.game_system_name=="Infinity":
            for match in Match.objects.filter(round__season=season):

                if match.player1.profile.user.username=='Bye' or  match.player2.profile.user.username=='Bye':

                    if match.player1.profile.user.username=='Bye':
                        player=match.player2
                    elif match.player2.profile.user.username=='Bye':
                        player=match.player1
                    
                    op=0
                    vp=0
                    rounds_played=0 #IF YOU ONLY PLAY ONE ROUND AND CLOSE A SEASON THIS WILL DIVIDE BY 0 :(
                    for player_match in Match.objects.filter(Q(player1=player) | Q(player2=player)):
                        has_bye=False
                        if player_match.player1==player:
                            score_list=player_match.player1_score.split(',')
                            op+=int(score_list[1])
                            vp+=int(score_list[2])
                            if player_match.player2.profile.user.username=='Bye':
                                has_bye=True
                        if player_match.player2==player:
                            score_list=player_match.player2_score.split(',')
                            op+=int(score_list[1])
                            vp+=int(score_list[2])
                            if player_match.player1.profile.user.username=='Bye':
                                has_bye=True
                        if not has_bye:
                            rounds_played+=1
                    num_rounds=Round.objects.filter(season=season).count()


                    if ((op*num_rounds)%(rounds_played-1)) != 0:
                        op=(op*num_rounds)/(rounds_played-1)+1
                    else:
                        op=(op*num_rounds)/(rounds_played-1)
                  
                    if ((vp*num_rounds)%(rounds_played-1)) != 0:
                        vp=(vp*num_rounds)/(rounds_played-1)+1
                    else:
                        vp=(vp*num_rounds)/(rounds_played-1)
                    
                    new_score_string=""+score_list[0]+","+int(op)+","+int(vp)
                    if match.player1==player:
                        match.player1_score=new_score_string
                    elif match.player2==player:
                        match.player2_score=new_score_string
                    match.save()

        # bye: add up all objective points the player earned
        # multiply the result by the number of rounds
        # divide the result by the number of rounds played (round up)
        # This is done for OP and VP

        season.season_active = False
        season.save()

        messages.success(
            self.request,
            'Season Closed')

        url = reverse('season details', args=[self.kwargs['pk'], slugify(
            Season.objects.get(pk=self.kwargs['pk']).league)])
        return redirect(url)


class SeasonDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """only staff or primary admins can delete leagues"""
    model = Season

    def test_func(self):
        """only primary admins and staff can edit"""
        try:
            season = Season.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff:
            return True

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False
        if self.request.user.profile.linked_admin_profile\
                in season.league.group.group_primary_admins.all():
            return True
        
        return False

    def get_success_url(self):
        url = reverse('group info', args=[
                      'region', self.object.league.group.slug(), self.object.league.group.id])

        return url


class SeasonView(FilterView):
    """
    displays group details, sidebar will show leagues
    also shows all images tagged with a goup season as source
    """
    model = UserImage
    filterset_class = ImageFilter
    context_object_name = 'images'
    paginate_by = 8
    template_name = 'League/season_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        season_var = Season.objects.get(pk=self.kwargs['pk'])

        image_filter = ImageFilter(
            self.request.GET, queryset=UserImage.objects.all())
        context['filter_form'] = image_filter
        context['season'] = season_var
        return context




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

    if automatic matchmaking fails a new round with no matches
    will be created and manual matchmaking will need to be used

    future development options exists to allow round delete to undo
    psf updates for the round (only when deleting most recent) to allow
    new attempts at autogeneration. this is not implemented right now
    because the intention is to have automatchmaking stable enough that
    it will only fail on rounds that require manual matchmaking.
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

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False
        if season.league in self.request.user.profile.linked_admin_profile.leagues_managed.all():
            return True
     
        return False

    def league_logic_test(self, request, *args, **kwargs):
        """
        tests if a new round is allowed to be created
        """

        season = Season.objects.get(pk=self.kwargs['pk'])
        leagues_seasons = season.league.child_season.all()

        url = reverse('season details', args=[self.kwargs['pk'], slugify(
        Season.objects.get(pk=self.kwargs['pk']).league)])

        if season.registration_active:
            messages.error(
                self.request,
                'Creating a round can only be done when registration is closed.')
            # redirect to the page to close registration instead of just bouncing
            url = reverse('edit season', args=[self.kwargs['pk']])
            return url
        
        for player in PlayerSeasonFaction.objects.filter(season=season).exclude(
            profile__user__username="Tie").exclude(profile__user__username="Bye"):
            if player.faction is None:
                messages.error(
                self.request,
                'There are players that do not have a faction assigned')
                # redirect to the page to close registration instead of just bouncing
                url = reverse('edit season', args=[self.kwargs['pk']])
                return url

        if leagues_seasons.count() > 1:
            iterate_var = 0
            for entry in leagues_seasons:
                if entry == season:
                    # if we start registration for a second season makeing a new round will result in a negative index
                    diff=iterate_var-1
                    if diff>=0:
                        if leagues_seasons[diff].season_active:
                            messages.error(
                                self.request,
                                'The previous season is still active')
                            return url
                    else:#we will only get here if there is only one season in the league
                        if not leagues_seasons[0].season_active:
                            messages.error(
                                self.request,
                                'The season is not active')
                            return url
                iterate_var += 1

        number_of_players = PlayerSeasonFaction.objects.filter(season=season).exclude(
            profile__user__username="Tie").exclude(profile__user__username="Bye").count()

        if season.seasons_rounds.count() >= number_of_players-1 and\
                season.allow_repeat_matches is False:
            messages.error(
                self.request,
                'There cannot be additional rounds without repeat matchups')
            return url

        round_list = season.seasons_rounds.all()
        if round_list:
            match_list = round_list.last().round_matches.all()
            if match_list:
                for match in match_list:
                    if not match.winner:
                        messages.error(
                            self.request,
                            'There are unresolved matches in the current round.')
                        return url
            else:
                messages.error(
                    self.request,
                    'The last round in unfinished.')
                return url

        return None

    def get(self, request, *args, **kwargs):
        """ensures you have closed registration before making new rounds"""

        redirect_url=self.league_logic_test(self, request, *args, **kwargs)
        if redirect_url:
            return redirect(redirect_url)
        

        return super().get(self, request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """ensures you have closed registration before making new rounds"""

        redirect_url=self.league_logic_test(self, request, *args, **kwargs)
        if redirect_url:
            return redirect(redirect_url)


        return super().post(self, request, *args, **kwargs)

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







                # should previous opponent be here or maybe in match saving with the matched state?

                # adding it to match save





            # for match in season.seasons_rounds.last().round_matches.all():
            #     match.player1.previous_opponents.add(match.player2)
            #     match.player1.score += match.player1_score
            #     match.player1.matched = False

            #     match.player2.previous_opponents.add(match.player1)
            #     match.player2.score += match.player2_score
            #     match.player2.matched = False

            #     if match.winner.profile.user.username == "Bye":
            #         match.player1.wlrecord += "B-"
            #         match.player2.wlrecord += "B-"
            #     elif match.winner == match.player1:
            #         match.player1.wlrecord += "W-"
            #         match.player2.wlrecord += "L-"
            #     elif match.winner == match.player2:
            #         match.player1.wlrecord += "L-"
            #         match.player2.wlrecord += "W-"
            #     else:
            #         match.player1.wlrecord += "T-"
            #         match.player2.wlrecord += "T-"

            #     match.player1.save()
            #     match.player2.save()

            form.instance.round_number = season.seasons_rounds.count()+1

        else:
            # if there are no rounds create the first round
            # and create matchmaking support players
            form.instance.round_number = 1

            if PlayerSeasonFaction.objects.filter(season=season).count() % 2 != 0\
                    and season.allow_repeat_matches is False:
                bye_psf = PlayerSeasonFaction(
                    profile=UserProfile.objects.get(user__username='Bye'), season=season)
                bye_psf.save()

            tie_psf = PlayerSeasonFaction(
                profile=UserProfile.objects.get(user__username='Tie'), season=season)
            tie_psf.save()

            leagues_seasons = season.league.child_season.all()

            if leagues_seasons.count() > 1:
                iterate_var = 0
                for entry in leagues_seasons:
                    if entry == season:
                        leagues_seasons[iterate_var-1].season_active = False
                        leagues_seasons[iterate_var-1].save()
                    iterate_var += 1

            season.season_active = True
            season.save()

        redirect_url = super().form_valid(form)

        if form.cleaned_data['automate_matchmaking']:

            auto_matches_result = auto_round_matches_basic(season)

            if auto_matches_result:
                form.add_error('automate_matchmaking', ValidationError(
                    (auto_matches_result), code='invalid'))
                return super().form_invalid(form)

        return redirect_url


class RoundEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """only staff and the primary admins can edit."""
    model = Round
    form_class = RoundForm

    def test_func(self):
        """must manage league to access"""

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False

        
        if (
                self.get_object().season.league
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
        
        if self.request.user.is_staff:
            return True

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False

        if (round_var.season.league
            in
                self.request.user.profile.linked_admin_profile.leagues_managed.all()):
            return True
        return False
    
    def get(self, request, *args, **kwargs):
        """ensures you do not make more rounds than the player count supports"""
        round_var = Round.objects.get(pk=self.kwargs['pk'])
        round_var = Round.objects.get(pk=self.kwargs['pk'])
        players_in_round=round_var.season.players_in_season.all().exclude(profile__user__username='Tie')
        players_in_round=players_in_round.exclude(dropped=True)
        max_matchups=len(players_in_round)/2

        if len(round_var.round_matches.all())>=max_matchups:
            messages.error(
                self.request,
                'This round has the maximum number of matches')
           
            url = reverse('round details', args=[self.kwargs['pk'], slugify(
        Round.objects.get(pk=self.kwargs['pk']).season.league)])
            return redirect(url)
        
        return super().get(self, request, *args, **kwargs)

    def form_valid(self, form):

        round_var = Round.objects.get(pk=self.kwargs['pk'])

        # group_id cannot be null so we must add it to the form info
        if form.cleaned_data['player1'] == form.cleaned_data['player2']:
            form.add_error('player2', ValidationError(
                ('A player cannot be matched against themselves'), code='invalid'))
            return super().form_invalid(form)

        if not round_var.season.allow_repeat_matches:
            if form.cleaned_data['player2']\
                    in form.cleaned_data['player1'].previous_opponents.all():
                form.add_error('player2', ValidationError(
                    ('These players have already been matched against each other'), code='invalid'))
                return super().form_invalid(form)

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
    

# for next time: add a view to drop a player and handle dropping/adding bye to keep numbers even.
#                   add a view to add player. probably have a psf save wl string check to see first round participated in to -have 'N/A-' or something
#                           if the player is given a starting score and the view also handles fixing byes everything else should just work with it.
# remember to test adding a player back in that you drop
 
class AddDropPlayer(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    allows a user to be added or removed from an active league season
    
    """
    def test_func(self):
        """must manage league or be staff to access"""
        try:
            season = Season.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff:
            return True

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False
        if season.league in self.request.user.profile.linked_admin_profile.leagues_managed.all():
            return True
        
        return False
    def get(self, request, *args, **kwargs):
        """expects no args"""
        season = Season.objects.get(pk=self.kwargs['pk'])
        form=AddDropPlayerForm(season=season)

        return render(request, 'League/add_drop.html',{'form': form})
    def post(self, request, *args, **kwargs):
        """adds or drops players"""
        season = Season.objects.get(pk=self.kwargs['pk'])
        success_url = reverse('season details', args=[self.kwargs['pk'], slugify(season.league)])
        form=AddDropPlayerForm(request.POST,season=season)
        if not form.is_valid():
            return render(request, 'League/add_drop.html',{'form': form})

        if form.cleaned_data["drop_players"] is None and form.cleaned_data["add_players"] is None:
            messages.success(
            self.request,
            'No data submitted')
            return redirect(success_url)
        
        drop_players=form.cleaned_data["drop_players"]
        add_players=form.cleaned_data["add_players"]
        change_bye_state=False

        if drop_players and add_players:
            if not (len(drop_players)+len(add_players))%2 == 0:
                change_bye_state=True
        elif drop_players and not add_players:
            if not len(drop_players)%2 == 0:
                change_bye_state=True
        elif not drop_players and add_players:
            if not len(add_players)%2 == 0:
                change_bye_state=True

        # we should check to see if the net result is even to save work on fiddling with bye player
        if drop_players:
            for player_id in drop_players:
                if season.registration_active:
                    player=PlayerSeasonFaction.objects.get(pk=player_id)
                    player.delete()
                else:
                    player=PlayerSeasonFaction.objects.get(pk=player_id)
                    player.dropped=True
                    player.save()
        


        added_psfs=[]
        if add_players:
            for player_id in add_players:
                player=UserProfile.objects.get(pk=player_id)
                var=PlayerSeasonFaction(profile=player,season=season)
                var.save()
                added_psfs+=[var]

               

        if change_bye_state and not season.registration_active:
            updated=False
            for player in PlayerSeasonFaction.objects.filter(season=season):
                if player.profile.user.username=='Bye':
                    if player.dropped:
                        player.dropped=False
                        updated=True
                        player.save()
                    else:
                        player.dropped=True
                        updated=True
                        player.save()
            if updated == False:
                player=UserProfile.objects.get(user__username="Bye")
                var=PlayerSeasonFaction(profile=player,season=season)
                var.save()



        if added_psfs:
            update_string=''
            first_item=added_psfs.pop(0)
            if len(added_psfs)==0:
                success_url = reverse('psf edit', args=[first_item.id])

            # for psf in added_psfs:
            #     update_string+=(str(psf.id)+',')
            for psf in added_psfs:
                if not update_string:
                    update_string = str(psf.id)
                else:
                    update_string += ','+str(psf.id)

            url = reverse('psf edit', args=[first_item.pk])
            url += f'?update_users={update_string}'
            success_url=url

        return redirect(success_url)

class CreateMatchAuto(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    will create matches for all remaining players in a league
    """
    def test_func(self):
        """must manage league or be staff to access"""
        try:
            season = Round.objects.get(pk=self.kwargs['pk']).season
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff:
            return True

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False
    
        if season.league in self.request.user.profile.linked_admin_profile.leagues_managed.all():
            return True
    
        return False
    
    
    
    
    def get(self, request, *args, **kwargs):
        """expects no args"""


        round_var = Round.objects.get(pk=self.kwargs['pk'])
        players_in_round=round_var.season.players_in_season.all().exclude(profile__user__username='Tie')
        players_in_round=players_in_round.exclude(dropped=True)
        max_matchups=len(players_in_round)/2


        if len(round_var.round_matches.all())>=max_matchups:
            messages.error(
                self.request,
                'This round has the maximum number of matches')
           
            url = reverse('round details', args=[self.kwargs['pk'], slugify(
                Round.objects.get(pk=self.kwargs['pk']).season.league)])
            return redirect(url)


        # add a check for  unmatched players  - does the check for max rounds acheive the same thing? probably?
        season=Round.objects.get(id=self.kwargs['pk']).season
        # unmatched_players=PlayerSeasonFaction.objects.filter(season=season).exclude(matched=True)
        # print('automatch get ran')
        # print(PlayerSeasonFaction.objects.filter(season=season))
        # print(unmatched_players)
        auto_matches_result = auto_round_matches_basic(season)

        if auto_matches_result:

            messages.error(
                self.request,
                f'{auto_matches_result}')

        else:
            messages.success(
            self.request,
            'Automatic matchmaking complete!')

        league_str=slugify(season.league.league_name)
        url = reverse('round details', args=[self.kwargs['pk'],league_str])

        return redirect(url)



class MatchEdit(UserPassesTestMixin, UpdateView):
    """
    updates PSF info on save
    """
    model = Match
    form_class = MatchEditForm

    def test_func(self):
        """
        Must be logged in and then: must be one of the two players in a match during the round or a league admin
        OR
        can be logged out but then must have the qr_code_key
        --
        Cannot progress if the maximum number of  matches for the round have not been created yet
        """

        try:
            match = Match.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error
        
        


        # checks for being logged out
        if not self.request.user.is_authenticated:
            code=self.request.GET.get('code')
            try:
                season=Season.objects.get(qr_code_key=code)
                if season != match.round.season:
                    return False
                if match.round.season.seasons_rounds.last() == match.round:
                    return True
                return False
            except ObjectDoesNotExist as error:
                return False

        # checks for being logged in

        if self.request.user.is_staff:
            return True


        if check_league_admin(match.round.season.league, self.request.user):
            return True

        # users in a match can edit results while the match is the most recent
        if match.player1.profile == self.request.user.profile\
                or match.player2.profile == self.request.user.profile:
            if match.round.season.seasons_rounds.last() == match.round:
                return True
            messages.error(
                self.request,
                'You can only edit results for the current round. \
                    Contact an Admin if old results are invalid.')
        return False

    def does_matchmaking_need_to_fail(self):
        """ 
        Cannot progress if the maximum number of  matches for the round have not been created yet
        returns false if it's safe to continue
        and a url to redirect to if not
        """
        match = Match.objects.get(pk=self.kwargs['pk'])
        all_matches_in_round=Match.objects.filter(round=match.round)
        number_of_players=PlayerSeasonFaction.objects.filter(season=match.round.season).exclude(profile__user__username='Tie').exclude(
        dropped=True).count()
        if all_matches_in_round.count() < number_of_players/2 :
            messages.error(
                self.request,
                'You cannot edit results until all matches have been created.')
            league_str=slugify(match.round.season.league.league_name)
            url = reverse('round details', args=[match.round.pk,league_str])
            return url
        return False

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        # print(self.form_class)
        # print(self.kwargs)
        # print(self.args)

        result=self.does_matchmaking_need_to_fail()
        if result:
            return redirect(result)

        return super().get(request, *args, **kwargs)
    
    def post(self,request,*args,**kwargs):
        result=self.does_matchmaking_need_to_fail()
        if result:
            return redirect(result)

        return super().post(request, *args, **kwargs)

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        # var=form_class(**self.get_form_kwargs(),initial={"player1_score":"5,5,5"})
        # form = form_class(**self.get_form_kwargs())
        # form=form.is_valid()
        # print(form)
        # print(form.cleaned_data)
        # print(form.fields['player1_score'])
        return form_class(**self.get_form_kwargs())


    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):

            saved_object=self.object
            p1_score=saved_object.player1_score.split(',')
            p2_score=saved_object.player2_score.split(',')
            p1_score.pop(0)
            p2_score.pop(0)
            p1_score=",".join(p1_score)
            p2_score=",".join(p2_score)
            # temp_object=Match(round=saved_object.round,player1=saved_object.player1,player2=saved_object.player2,winner=saved_object.winner,player1_score=p1_score,player2_score=p2_score,player1_list=saved_object.player1_list,player2_list=saved_object.player2_list)


            # change the score without saving the object so that the form has the values the user cares about
            self.object.player1_score=p1_score
            self.object.player2_score=p2_score

            kwargs.update({'instance': self.object})
        kwargs.update({
            'player1': self.object.player1,
            'player2': self.object.player2
        })
        # print(kwargs)
        return kwargs

    def form_valid(self, form):


        # if there is not a tie no special processing neeeds to occur
        if form.cleaned_data['winner'].profile.user.username != "Tie":
            return super().form_valid(form)

        # might need system specific scoring checks right here. For now first number is score which must match
        

        img_list1 = form.cleaned_data['player1_score'].split(',')
        img_list2= form.cleaned_data['player2_score'].split(',')


        if img_list1[0] != img_list2[0]:
            form.add_error('player2_score', ValidationError(
                ('Players must have the same score on a Tie'), code='invalid'))
            return super().form_invalid(form)

        return super().form_valid(form)


class MatchDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """only staff or primary admins can delete leagues"""
    model = Match

    def test_func(self):
        """must manage league to access"""
        try:
            match = Match.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if not AdminProfile.objects.filter(userprofile__user=self.request.user):
            return False

        
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
        context['match_images'] = UserImage.objects.filter(match=self.object)

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
    
class SubmitResultsCode(View):
    """
    authenticates a qrcode url, if a match is also given it will redirect to match result submission passing along the code
    """

    def get(self, request, *args, **kwargs):
        """
        checks for the args code and match
        if code is valid returns a list of matches for the latest round of the event with the code
        if code and match are valid redirects to edit match
        edit match handles validation this function only checks if the code matches any season
        """

        code=self.request.GET.get('code')
        match=self.request.GET.get('match')

        try:
           season=Season.objects.get(qr_code_key=code)
        except:
            return render(request, 'League/submit_results_code.html')

        if match:
            try:
                match_object=Match.objects.get(pk=match)              
                url = reverse('edit match', args=[match_object.id])
                url=url+"?code="+str(code)
                return redirect(url)
            except:
                pass
            
        matches=Match.objects.filter(round=season.seasons_rounds.all().last())

        return render(request, 'League/submit_results_code.html',
                      {'matches': matches})


class MatchImageUpload(UserPassesTestMixin, GalleryMultipleUpload):
    """
    GalleryMultipuleUpload will handle setting the image as official
    and sending signals as long as we set
    studio_official_upload to True to enable the functionality

    Only staff and studio admin can upload
    """
    match_upload = True
    form_class = MatchUploadMultipleImages

    def test_func(self):
        return match_permission_check(Match.objects.get(pk=self.kwargs['pk']), self.request.user)

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update({
            'source': Match.objects.get(pk=self.kwargs['pk']).round.season
        })
        return kwargs


class MatchImageUploadMultipart(UserPassesTestMixin, GalleryUploadMultipart):
    """
    GalleryMultipuleMultipart will handle setting the image as official
    and sending signals as long as we set studio_official_upload
    to True to enable the functionality

    Only staff and studio admin can upload
    """
    match_upload = True
    form_class = MatchUploadMultipartImages

    def test_func(self):
        return match_permission_check(Match.objects.get(pk=self.kwargs['pk']), self.request.user)

    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update({
            'source': Match.objects.get(pk=self.kwargs['pk']).round.season
        })
        return kwargs



class PSFView(DetailView):
    """Viewing Matches is public"""
    model = PlayerSeasonFaction

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # season_var = Season.objects.get(season=self.kwargs['pk'])
        season_var= self.get_object().season


        context['season'] = season_var
        return context
    
class PSFEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """only staff and the primary admins can edit."""
    model = PlayerSeasonFaction
    form_class = PSFUpdateForm

    def test_func(self):

        try:
            psf = PlayerSeasonFaction.objects.get(pk=self.kwargs['pk'])
        except ObjectDoesNotExist as error:
            raise Http404(f'{error}') from error

        if self.request.user.is_staff:
            return True

        if not (self.request.user == psf.profile.user):
            
            if check_league_admin(psf.season.league, self.request.user):
                return True

            return False

        if not psf.season.registration_active:
            return False

        return True
    
    def get_form_kwargs(self):
        """Return the keyword arguments for instantiating the form."""
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.object})
        kwargs.update({
            'league': self.object.season.league
        })
        return kwargs
    
    def get_success_url(self):

        if self.request.method == "POST":
            pklist = self.request.GET.get('update_users')
            if pklist:
                pklist = pklist.split(',')
                next_user=pklist.pop(0)
                if pklist:
                    url = reverse('psf edit', args=[next_user])
                    print(pklist)
                    string=','.join(pklist)
                    print(string)
                    url += f'?update_users={string}'
                    print(url)
                    return url
                url = reverse('psf edit', args=[next_user])
                return url

        return super().get_success_url()