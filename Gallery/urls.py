from django.urls import path

from .views import *


# app_name= 'League' #does this need to be here?

urlpatterns = [

# path('', views.leagues, name='gallery home'),

# path('', Gallery_home.as_view(), name='gallery home'),
path('', GalleryListView.as_view(), name='gallery home'),
# path("old", GallelryListViewOld.as_view(), name="gallery home old"),
path('upload',GalleryUpload.as_view(),name='gallery upload'),
path('upload/multipart',GalleryUploadMultipart.as_view(),name='gallery upload multipart'),
path('upload/multipart/confirm',GalleryUploadMultipartConfirm.as_view(),name='gallery upload multipart confirm'),
path('upload/multi',GalleryMultipleUpload.as_view(),name='gallery multiple upload'),
path('image/multi/update',GalleryMultipleUpdate.as_view(),name='gallery multiple update'),
# path('filter', GalleryFilterListView.as_view(), name='gallery filter'),
path('image/<int:pk>/', GalleryDetailView.as_view(), name='image details'),
path('image/<int:pk>/like', GalleryDetailUpvoteView.as_view(), name='image upvote'),
path('image/<int:pk>/update', GalleryUpdate.as_view(), name='image update'),
path('image/<int:pk>/subimage/update', GallerySubImageUpdate.as_view(), name='subimage update'),
path('image/<int:pk>/delete', GalleryDelete.as_view(), name='image delete'),
#
path('manage_image_fields',Manage_image_fields.as_view(), name='manage image fields'),
path('colour/add',ColourCreate.as_view(),name='add colour'),
path('colour/<int:pk>/delete', ColourDelete.as_view(), name='delete colour'),
path('colour_priority/add',ColourPriorityCreate.as_view(),name='add colour priority'),
path('colour_priority/<int:pk>/delete', ColourPriorityDelete.as_view(), name='delete colour priority'),
# path('unit_type/add',unit_type_Create.as_view(),name='add unit type'),
# path('professional/add',professional_Create.as_view(),name='add professional'),
# path('country/add',CountryCreate.as_view(),name='add country'),
# path('region/add',RegionCreate.as_view(),name='add region'),
# path('city/add',CityCreate.as_view(),name='add city'),
#
# path('colour/create', ColourCreatePopup, name = "ColourCreate"),
# path('colour_catagory/create', ColourCatagoryCreatePopup, name = "ColourCatagoryCreate"),


]
