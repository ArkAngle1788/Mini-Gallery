
from django.urls import path

from .views import Profile, ProfileUpdate, SelfProfile

urlpatterns = [


path('', SelfProfile.as_view(), name='profile self'),
path('<int:pk>', Profile.as_view(), name='profile'),
path('<int:pk>/update', ProfileUpdate.as_view(), name='profile update'),


]
