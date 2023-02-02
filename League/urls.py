from django.urls import path

# from . import views
from .views import (LeagueCreate, LeagueDelete, LeagueEdit, LeagueView,
                    SeasonCreate, SeasonDelete, SeasonEdit, SeasonView,
                    SeasonRegister, SeasonClose, RoundCreate, RoundEdit, RoundView,
                    MatchCreateManual, MatchEdit, MatchDelete, MatchView,
                    SubmitResults,leagues)

urlpatterns = [

path('', leagues, name='leagues'),
path('<int:pk>/create', LeagueCreate.as_view(),name='create league'),
path('<int:pk>/edit', LeagueEdit.as_view(),name='edit league'),
path('delete/<int:pk>', LeagueDelete.as_view(),name='delete league'),
path('<int:pk>/<str:league>', LeagueView.as_view(), name='league details'),
path('season/<int:pk>/create', SeasonCreate.as_view(), name='create season'),
path('season/<int:pk>/edit', SeasonEdit.as_view(), name='edit season'),
path('season/<int:pk>/delete', SeasonDelete.as_view(), name='delete season'),
path('season/<int:pk>/close', SeasonClose.as_view(), name='close season'),
path('season/<int:pk>/<str:league>/', SeasonView.as_view(), name='season details'),
path('season/<int:pk>/<str:league>/register',SeasonRegister.as_view(),name='season register'),
path('season/round/<int:pk>/create', RoundCreate.as_view(), name='create round'),
path('season/round/<int:pk>/edit', RoundEdit.as_view(), name='edit round'),
path('season/round/<int:pk>/<str:league>',RoundView.as_view(), name='round details'),
path('season/round/match/<int:pk>/manual_match',MatchCreateManual.as_view(),name='create match'),
path('season/round/match/<int:pk>/edit', MatchEdit.as_view(), name='edit match'),
path('season/round/match/<int:pk>/delete', MatchDelete.as_view(), name='delete match'),
path('season/round/match/details/<int:pk>/<str:league>',MatchView.as_view(), name='match details'),
path('season/round/match/submit_results',SubmitResults.as_view(),name='submit results'),


]
