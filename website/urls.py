"""website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from CommunityInfrastructure import views as infrastrucure_views

#following two imports are for images to work (so urls can map to uploaded images)
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("select2/", include("django_select2.urls")),
    path('', include('CommunityInfrastructure.urls')),
    path('leagues/', include('League.urls')),
    path('gallery/', include('Gallery.urls')),
    path('gamedata/',include('GameData.urls')),
    path('news&content/',include('ContentPost.urls')),
#     path('accounts/login/', account_views.login,name="account_login" ),
    path('accounts/', include('allauth.urls')),
    path('accounts/profile/', include('UserAccounts.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




#     path('profile/', include('UserAccounts.urls')),
#
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
