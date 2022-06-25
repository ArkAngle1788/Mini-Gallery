
from django.urls import path

from .views import *

urlpatterns = [


path('', Self_Profile.as_view(), name='profile self'),
path('<int:pk>', Profile.as_view(), name='profile'),
path('<int:pk>/update', ProfileUpdate.as_view(), name='profile update'),


]
