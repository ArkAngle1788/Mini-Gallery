from django.urls import path

from .views import *


# app_name= 'League' #does this need to be here?

urlpatterns = [


# path('', Gallery_home.as_view(), name='gallery home'),
path('', ContentPostListView.as_view(), name='blog list'),
path('post/<int:pk>/',ContentPostDetailView.as_view(),name='blog detail'),
path('post/new/',ContentPostCreateView.as_view(),name='blog create'),
path('post/<int:pk>/edit/',ContentPostUpdateView.as_view(),name='blog update'),
path('post/<int:pk>/delete/',ContentPostDeleteView.as_view(),name='blog delete'),


]
