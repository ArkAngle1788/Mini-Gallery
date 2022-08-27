from django.urls import path

from .views import (ApproveUser, CityCreate, CountryCreate, Group,
                    GroupAddAdmin, GroupCreate, GroupDelete, GroupEdit,
                    GroupRemoveAdmin, GroupsByZone, GroupsTop, RegionCreate,
                    StudioCreate, StudioDetails, StudioEdit, StudioExport,
                    StudioRequestFacebook, StudioRequestInstagram,
                    StudioUpload, StudioUploadMultipart, about, contact, home,
                    privacy_policy)

urlpatterns = [
    path('', home, name='home'),
    path('about',about,name='about'),
    path('contact',contact,name='contact'),
    path('privacy_policy',privacy_policy,name='privacy policy'),

    path('organizations', GroupsTop.as_view(), name='groups top'),
    path('organizations/create', GroupCreate.as_view(),name='create group'),
    path('organizations/<str:zone>/<slug:group_slug>/<int:pk>/edit', GroupEdit.as_view(),name='edit group'),
    path('organizations/delete/<int:pk>', GroupDelete.as_view(),name='delete group'),
    path('organizations/approve_user',ApproveUser.as_view(),name='approve user'),

    path('organizations/paintingstudio/create', StudioCreate.as_view(),name='create painting studio'),
    path('organizations/paintingstudio/edit/<int:pk>', StudioEdit.as_view(),name='edit painting studio'),
    path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>', StudioDetails.as_view(),name='painting studio'),
    path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>/uploadimages', StudioUpload.as_view(),name='painting studio upload'),
    path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>/uploadmultipartimages', StudioUploadMultipart.as_view(),name='painting studio multipart upload'),
    path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>/exportsocial',StudioExport.as_view(),name='studio export'),
    path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>/exportfacebook',StudioRequestFacebook.as_view(),name='studio request facebook'),
    path('organizations/paintingstudio/<slug:studio_slug>/<int:pk>/exportinstagram',StudioRequestInstagram.as_view(),name='studio request instagram'),

    path('organizations/<str:zone>/', GroupsByZone.as_view(), name='groups by zone'),
    path('organizations/<str:zone>/<slug:group_slug>/<int:pk>', Group.as_view(), name='group info'),
    path('organizations/<str:zone>/<slug:group_slug>/<int:pk>/add_admin', GroupAddAdmin.as_view(), name='group add admin'),
    path('organizations/<str:zone>/<slug:group_slug>/<int:pk>/remove_admin', GroupRemoveAdmin.as_view(), name='group remove admin'),

    path('country/add',CountryCreate.as_view(),name='add country'),
    path('region/add',RegionCreate.as_view(),name='add region'),
    path('city/add',CityCreate.as_view(),name='add city'),

    ]

#NOTICE: painting studio must be above group views b/c string matching will cause painting studio to map to group detail pages if we check for them first
