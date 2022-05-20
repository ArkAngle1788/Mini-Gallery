from django.urls import path

from . import views


# app_name= 'League' #does this need to be here?

urlpatterns = [

path('', views.leagues, name='leagues'),
# # path('<str:league>/', views.league_details, name='league details'),
# path('<str:league>/', League_details.as_view(), name='league details'),
# # path('view_league',views.view_league,name='view league'),
# path('manage_leagues',views.manage_leagues,name='manage leagues'),
# path('manage_leagues_original',views.manage_leagues_original, name='manage leagues original'),
# path('new_league',views.new_league, name= 'new league'),
# path('league_activation',views.league_activation, name='league activation'),
# # path('basic_matchmaking',views.basic_matchmaking, name='basic matchmaking'),
# path('create_matchup',views.create_matchup, name='create matchup'),#this is the view in charge of matchmaking now
# path('new_round',views.create_round_matchup, name='new round'),
# path('new_season',views.new_season, name='new season'),
# path('matchup_created',views.save_matchup, name='save matchup'),
# path('submit_results',views.submit_results, name='submit results'),
# path('save_results',views.save_results, name='save results'),
# path('save_season',views.save_season, name='save season'),
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
