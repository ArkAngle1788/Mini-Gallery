from django.urls import path

from .views import *


urlpatterns = [
    path('', home, name='home'),
    path('about',about,name='about'),
    path('contact',contact,name='contact'),
    path('organizations', Groups_top.as_view(), name='groups top'),
    path('organizations/create', Group_Create.as_view(),name='create group'),
    path('organizations/delete/<int:pk>', Group_Delete.as_view(),name='delete group'),
    path('organizations/paintingstudio/create', Studio_Create.as_view(),name='create painting studio'),
    path('organizations/paintingstudio/edit/<int:pk>', Studio_Edit.as_view(),name='edit painting studio'),
    path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>', Studio_Details.as_view(),name='painting studio'),
    path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>/uploadimages', Studio_Upload.as_view(),name='painting studio upload'),
    # path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>/testview', Studio_Request.as_view(),name='studio request'),
    path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>/exportsocial',Studio_Export.as_view(),name='studio export'),
    path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>/exportfacebook',Studio_Request_Facebook.as_view(),name='studio request facebook'),
    path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>/exportinstagram',Studio_Request_Instagram.as_view(),name='studio request instagram'),
    path('organizations/<str:zone>/', Groups_by_zone.as_view(), name='groups by zone'),
    path('organizations/<str:zone>/<slug:group_slug>/<int:pk>', Group.as_view(), name='group info'),
    path('organizations/<str:zone>/<slug:group_slug>/<int:pk>/add_admin', Group_add_admin.as_view(), name='group add admin'),
    path('organizations/<str:zone>/<slug:group_slug>/<int:pk>/remove_admin', Group_remove_admin.as_view(), name='group remove admin'),

    path('country/add',Country_Create.as_view(),name='add country'),
    path('region/add',Region_Create.as_view(),name='add region'),
    path('city/add',City_Create.as_view(),name='add city'),

    ]

#NOTICE: painting studio must be above group views b/c the groupview path with variables doesn't care about that the str variables are and will cause painting studio to map to group detail pages if we check for them first
