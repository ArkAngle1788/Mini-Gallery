from django.urls import path

from .views import (ColourCreate, ColourDelete, ColourPriorityCreate,
                    ColourPriorityDelete, GalleryDelete,
                    GalleryDetailUpvoteView, GalleryDetailView,
                    GalleryListView, GalleryMultipleUpdate,
                    GalleryMultipleUpload, GallerySubImageUpdate,
                    GalleryUpdate, GalleryUpload, GalleryUploadMultipart,
                    GalleryUploadMultipartConfirm, ManageImageFields)

urlpatterns = [

path('', GalleryListView.as_view(), name='gallery home'),
path('upload',GalleryUpload.as_view(),name='gallery upload'),
path('upload/multipart',GalleryUploadMultipart.as_view(),name='gallery upload multipart'),
path('upload/multipart/confirm',GalleryUploadMultipartConfirm.as_view(),name='gallery upload multipart confirm'),
path('upload/multi',GalleryMultipleUpload.as_view(),name='gallery multiple upload'),
path('image/multi/update',GalleryMultipleUpdate.as_view(),name='gallery multiple update'),
path('image/<int:pk>/', GalleryDetailView.as_view(), name='image details'),
path('image/<int:pk>/like', GalleryDetailUpvoteView.as_view(), name='image upvote'),
path('image/<int:pk>/update', GalleryUpdate.as_view(), name='image update'),
path('image/<int:pk>/subimage/update', GallerySubImageUpdate.as_view(), name='subimage update'),
path('image/<int:pk>/delete', GalleryDelete.as_view(), name='image delete'),
#
path('manage_image_fields',ManageImageFields.as_view(), name='manage image fields'),
path('colour/add',ColourCreate.as_view(),name='add colour'),
path('colour/<int:pk>/delete', ColourDelete.as_view(), name='delete colour'),
path('colour_priority/add',ColourPriorityCreate.as_view(),name='add colour priority'),
path('colour_priority/<int:pk>/delete', ColourPriorityDelete.as_view(), name='delete colour priority'),

]
