from django.urls import path

# from . import views
from .views import (LeagueCreate, LeagueDelete, LeagueEdit, LeagueView,
                    SeasonCreate, SeasonDelete, SeasonEdit, SeasonView,
                    SeasonRegister, RoundCreate, RoundEdit, RoundView,
                    MatchCreateManual, MatchEdit, MatchDelete, MatchView,
                    leagues)

urlpatterns = [

path('', leagues, name='leagues'),
path('<int:pk>/create', LeagueCreate.as_view(),name='create league'),
path('<int:pk>/edit', LeagueEdit.as_view(),name='edit league'),
path('delete/<int:pk>', LeagueDelete.as_view(),name='delete league'),
path('<int:pk>/<str:league>', LeagueView.as_view(), name='league details'),
path('season/<int:pk>/create', SeasonCreate.as_view(), name='create season'),
path('season/<int:pk>/edit', SeasonEdit.as_view(), name='edit season'),
path('season/<int:pk>/delete', SeasonDelete.as_view(), name='delete season'),
path('season/<int:pk>/<str:league>/', SeasonView.as_view(), name='season details'),
path('season/<int:pk>/<str:league>/register',SeasonRegister.as_view(),name='season register'),
path('season/round/<int:pk>/create', RoundCreate.as_view(), name='create round'),
path('season/round/<int:pk>/edit', RoundEdit.as_view(), name='edit round'),
path('season/round/<int:pk>/<str:league>',RoundView.as_view(), name='round details'),
path('season/round/match/<int:pk>/manual_match',MatchCreateManual.as_view(),name='create match'),
path('season/round/match/<int:pk>/edit', MatchEdit.as_view(), name='edit match'),
path('season/round/match/<int:pk>/delete', MatchDelete.as_view(), name='delete match'),
path('season/round/match/details/<int:pk>/<str:league>',MatchView.as_view(), name='match details'),


# path('manage_leagues',views.manage_leagues,name='manage leagues'),
# path('manage_leagues_original',views.manage_leagues_original, name='manage leagues original'),
# path('new_league',views.new_league, name= 'new league'),
# path('league_activation',views.league_activation, name='league activation'),
# # path('basic_matchmaking',views.basic_matchmaking, name='basic matchmaking'),
# path('create_matchup',views.create_matchup, name='create matchup'),#this is the view in charge of matchmaking now
# path('new_round',views.create_round_matchup, name='new round'),

# path('matchup_created',views.save_matchup, name='save matchup'),
# path('submit_results',views.submit_results, name='submit results'),
# path('save_results',views.save_results, name='save results'),

# path('register_for_league',views.league_signup,name='league signup'),
#
# path('edit_round/<int:pk>', RoundUpdateView.as_view(), name='round update'),
# path('system/add', SystemCreate.as_view(), name='add system'),
# path('faction_type/add', Faction_TypeCreate.as_view(), name='add faction type'),
# path('faction/add', FactionCreate.as_view(), name='add faction'),
# path('sub_faction/add', Sub_factionCreate.as_view(), name='add sub faction'),
#
# path('league/<int:pk>/delete',LeagueDelete.as_view(),name='league delete'),

]
