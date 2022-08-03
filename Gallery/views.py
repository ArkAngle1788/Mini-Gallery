from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .models import Conversion, Scale_Of_Image, Colour, Colour_Priority,  Colour_Catagory, UserImage, UserSubImage, TempImage,sub_get_upload_to,get_upload_to
from ContentPost.custom_functions import calculate_news_bar
from CommunityInfrastructure.models import Country, Region, City, PaintingStudio
from GameData.models import Unit_Type,Faction_Type,Faction,Sub_Faction
from League.models import League

import os
from django.views import View
from django.views.generic.edit import FormMixin
from django.views.generic import ListView, DetailView, UpdateView, DeleteView
from django.views.generic.edit import CreateView

from .forms import *
from django.core import serializers

from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin,PermissionRequiredMixin
from django.contrib.auth.decorators import login_required

from django.urls import reverse_lazy,reverse
from django.http import HttpResponse,Http404
from django.contrib import messages
from django.core.files.storage import default_storage #allows us to delete from google cloud because we've reconfigured that as the default

from django.db.models import Count #used for sorting likes

from .filters import ImageFilter


from django_filters.views import FilterView

from google.cloud import storage


class GalleryListView(FilterView):
    model=UserImage
    filterset_class=ImageFilter
    template_name='Gallery/gallery_home.html'
    context_object_name='images'
    paginate_by=8


    def get_context_data(self, *, object_list=None, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter

        if self.request.GET:
            dic_string=dict(self.request.GET)
            if self.request.GET.get('page'):
                dic_string.pop('page')
            context['search']=dic_string

        return context

class GalleryUpload(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=UserImage
    form_class=UploadImages
    permission_required=("Gallery.add_userimage")

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        return context

    def form_valid(self,form):
        form.instance.uploader=self.request.user #add this data first then validate
        return super().form_valid(form) # then run original form_valid

class GalleryUploadMultipart(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=UserImage
    form_class=UploadImagesMultipart
    permission_required=("Gallery.add_userimage")
    image_choices=[]

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        return context

    def form_valid(self,form):
        self.image_choices=[]
        form.instance.uploader=self.request.user #add this data first then validate
        object=super().form_valid(form) # then run original form_valid
        files = self.request.FILES.getlist('subimage')

        for img in files:
            subimage=TempImage(image=img,uploader=self.request.user)
            subimage.save()
            self.image_choices+=[subimage]
        self.object.image=self.image_choices[0].image
        self.object.save()
        return object

    def post(self, request, *args, **kwargs):
        self.object = None

        form = self.get_form()
        if form.is_valid():
            self.form_valid(form)
        else:
            return self.form_invalid(form)

        item_list=''
        item_list+=str(self.image_choices.pop(0))
        for option in self.image_choices:
            item_list+=','+str(option.pk)

        url=reverse('gallery upload multipart confirm')
        url+='?'+f'images={item_list}&main={self.object.pk}'
        return redirect(url)


class GalleryUploadMultipartConfirm(PermissionRequiredMixin,LoginRequiredMixin,View):
    permission_required=("Gallery.add_userimage")

    def get(self, request, *args, **kwargs):
        try:
            main=UserImage.objects.get(pk=self.request.GET.get('main'))
            if self.request.user != main.uploader:
                messages.error(request, f'Invalid Permissions')
                url=reverse('gallery home')+'?order=popularity'
                return redirect(url)
            strlist=self.request.GET.get('images').split(',')
            image_choices=TempImage.objects.filter(id__in=strlist)
        except :
            return render(request, 'error.html',{"error":'bad request'})

        for image in image_choices:
            if image.uploader!=self.request.user:
                messages.error(request, f'Invalid Permissions')
                url=reverse('gallery home')+'?order=popularity'
                return redirect(url)

        return render(request, 'Gallery/upload_sub_confirm.html',{"images":image_choices,'main':main.pk})

    def post(self, request, *args, **kwargs):
        try:
            main=UserImage.objects.get(pk=self.request.POST.get('main'))
            if self.request.user != main.uploader:
                messages.error(request, f'Invalid Permissions')
                url=reverse('gallery home')+'?order=popularity'
                return redirect(url)
            image_choices=TempImage.objects.filter(id__in=self.request.POST.get('image_list').split(','))
        except :
            return render(request, 'error.html',{"error":'bad data'})

        for image in image_choices:
            if image.uploader==self.request.user:
                pass
            else:
                messages.error(request, f'Invalid Permissions')
                url=reverse('gallery home')+'?order=popularity'
                return redirect(url)
        try:
            main_image=image_choices.get(pk=self.request.POST.get('image_select'))
        except:
            return render(request, 'error.html',{"error":'bad data'})

        image_choices=image_choices.exclude(pk=main_image.pk)

        for img in image_choices:
            imagename_str=sub_get_upload_to()+'/'+os.path.basename(img.image.name)
            subimage=UserSubImage(image=img.image,image_title=main.image_title,parent_image=main)
            # this bit is just here to make the development server play nice
            cloud=False
            try:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS']
                cloud=True
            except:
                pass

            if cloud:
                copy_blob('mini-gallery',img.image.name,'mini-gallery',imagename_str)
            else:
                default_storage.save(imagename_str, img.image)

            subimage.image=imagename_str
            subimage.save()
            img.image.close()


        imagename_str=get_upload_to()+'/'+os.path.basename(main_image.image.name)

        # this bit is just here to make the development server play nice
        cloud=False
        try:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS']
            cloud=True
        except:
            pass
        if cloud:
            copy_blob('mini-gallery',main_image.image.name,'mini-gallery',imagename_str)
        else:
            default_storage.save(imagename_str, main_image.image)
        main.image=imagename_str
        main.save()
        main_image.image.close()

        for img in TempImage.objects.filter(id__in=self.request.POST.get('image_list').split(',')):
            image_name=img.image.name
            default_storage.delete(image_name)

        url=main.get_absolute_url()
        return redirect(url)

# copy on google cloud storages, from their documentation
def copy_blob(bucket_name, blob_name, destination_bucket_name, destination_blob_name):
    #"""Copies a blob from one bucket to another with a new name."""
    # bucket_name = "your-bucket-name"
    # blob_name = "your-object-name"
    # destination_bucket_name = "destination-bucket-name"
    # destination_blob_name = "destination-object-name"

    storage_client = storage.Client()

    source_bucket = storage_client.bucket(bucket_name)
    source_blob = source_bucket.blob(blob_name)
    destination_bucket = storage_client.bucket(destination_bucket_name)

    blob_copy = source_bucket.copy_blob(source_blob, destination_bucket, destination_blob_name)



class GalleryMultipleUpload(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=UserImage
    form_class=UploadMultipleImages
    permission_required=("Gallery.add_userimage")
    success_url = reverse_lazy('gallery multiple update')
    uploadedimagelist=''

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        context['multi']=True

        return context

    def get_success_url(self):
        url=super().get_success_url()
        return url+"?images="+self.uploadedimagelist

    def form_valid(self,form):  #a view in CommunityInfrastructure overrides this function. changes here might need to be reflected there as well -- could extend the function to take a custom parameter that would determine which code to resolve and then it could be in one spot
        form.instance.uploader=self.request.user #add this data first then validate
        files = self.request.FILES.getlist('image')

        for f in files:
            form.instance.image=f
            newimage=form.save(commit=False)
            newimage.pk=None
            newimage.save()
            form.save_m2m()

            if self.uploadedimagelist == '' :
                self.uploadedimagelist+=str(newimage.pk)
            else:
                self.uploadedimagelist+=','
                self.uploadedimagelist+=str(newimage.pk)

        self.object=newimage#this stayed here b/c the createview class needs an object to bind to but it doesn't matter which one b/c we've changed functionality so much

        return FormMixin.form_valid(self,form) # then run original form_valid


class GalleryMultipleUpdate(PermissionRequiredMixin,LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=UserImage
    form_class=UploadImages
    permission_required=("Gallery.change_userimage")

    def test_func(self):
        if self.request.user.is_staff or self.get_object().uploader==self.request.user:
            return True
        return False

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        if self.request.method == 'POST':
            queryset = queryset.filter(pk=self.request.POST.get('imagepk'))
        if self.request.method == 'GET':
            if not self.request.GET.get('images'):
                raise Http404(f'error: {queryset.model._meta.verbose_name} has not been called correctly')
            pklist=self.request.GET.get('images')
            pklist=pklist.split(',')

            try:
                queryset = queryset.filter(pk=pklist[0])
            except:
                raise Http404(f'error: {queryset.model._meta.verbose_name} has not been called correctly you hacker')

        try:
             # Get the single item from the filtered queryset
             obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(f'error: {queryset.model._meta.verbose_name} has not been called correctly')
        return obj

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        context['image']=self.object
        if self.request.method=="GET":
            pklist=self.request.GET.get('images')
            pklist=pklist.split(',')
            pklist.pop(0)
            pkliststr=None
            for i in pklist:#we reformat this so that we don't end up with nested list maddness when this gets called multipule times on the same url args
                if not pkliststr:
                    pkliststr=str(i)
                else:
                    pkliststr+=','+str(i)
            context['remaining_images']=pkliststr
        return context

    def form_valid(self,form,original_name):
        self.object = form.save()

        if original_name != self.object.image.name:
            default_storage.delete(original_name)

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # form.is_valid() overrites self.object if it returns true. so we have to note the original name here so we can delete it after committing the new one
        original_name=self.object.image.name
        form = self.get_form()
        if form.is_valid():
            # form valid will commit the changes to the DB
            return self.form_valid(form,original_name)
        else:
            return self.form_invalid(form)


    # these values are not actually needed each step of the loop since we send them in the form. The initial check wants them in the url though and for now i'm leaving it like that b/c it's easier and also allows the user to look at the url to see how many more they have left.
    def get_success_url(self):

        if self.request.method=="POST":
            if self.request.POST.get('remaining_images'):
                url=reverse('gallery multiple update')
                url+=f'?images={self.request.POST.get("remaining_images")}'
                return url

        return super().get_success_url()

class GalleryUpdate(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=UserImage
    form_class=UploadImages

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        # form.is_valid() overrites self.object if it returns true. so we have to note the original name here so we can delete it after committing the new one
        original_name=self.object.image.name

        form = self.get_form()

        if form.is_valid():
            # form valid will commit the changes to the DB
            return self.form_valid(form,original_name)
        else:
            return self.form_invalid(form)


    def form_valid(self,form,original_name):
        self.object = form.save()

        if original_name != self.object.image.name:
            default_storage.delete(original_name)

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['current_subimages']=UserSubImage.objects.filter(parent_image__pk=self.object.pk)
        context['subimage_form']=UpdateSubImages(self.object.pk)
        context['image']=self.object
        return context

    def get_success_url(self):
        url=super().get_success_url()
        url+='?'
        for key in self.request.GET:
            url+=key+'='+self.request.GET[key]+'&'
        return url

    def test_func(self):
        if self.request.user.is_staff or self.get_object().uploader==self.request.user:
            return True
        return False

class GallerySubImageUpdate(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=UserImage
    form_class=UpdateSubImages
    template_name='Gallery/sub_image_update.html'

    def test_func(self):
        if self.request.user.is_staff or self.get_object().uploader==self.request.user:
            return True
        return False
    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        if form_class is None:
            form_class = self.get_form_class()
        kwargs=self.get_form_kwargs()
        kwargs.update({
            'parent_pk': self.object.pk
        })
        return form_class(**kwargs)
    def form_valid(self, form):
        """If the form is valid, save the associated model."""

        delete_me=UserSubImage.objects.filter(pk__in=form.data.getlist('sub'))
        for img in delete_me:
            image_name=img.image.name
            default_storage.delete(image_name)
            img.delete()
        for img in self.request.FILES.getlist('image'):
            newimage=UserSubImage(image=img,image_title=self.object.image_title,parent_image=self.object)
            newimage.save()
        url=self.object.get_absolute_url()
        return redirect(url)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        # context['news']=calculate_news_bar()
        context['current_subimages']=UserSubImage.objects.filter(parent_image__pk=self.object.pk)
        return context

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(form=form))

class GalleryDelete(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=UserImage
    success_url=reverse_lazy('gallery home')  # Note from docs:    We have to use reverse_lazy() instead of reverse(), as the urls are not loaded when the file is imported.

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        return context

    def form_valid(self,form):
        object=self.get_object()

        #a warning appeared when this was in the delete function saying to move custom delete logic here so it lives here now.
        if object.image:#actually deletes the image file instead of just dereferencing it
            image_name=object.image.name
            default_storage.delete(image_name)

            for img in object.sub_image.all():
                sub_image_name=img.image.name
                default_storage.delete(sub_image_name)

        #copied code from original form_valid
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

    def test_func(self):
        if self.request.user.is_staff or self.get_object().uploader==self.request.user:
            return True
        return False

class GalleryDetailView(DetailView):
    model=UserImage
    context_object_name='image'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        liked=False
        if self.request.user.is_authenticated:
            if self.request.user.liked_images.all().filter(pk=self.kwargs['pk']):
                liked=True
            context['liked']=liked

        newimage=self.object

        return context

class GalleryDetailUpvoteView(DetailView):
    model=UserImage
    context_object_name='image'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter

        if self.request.GET.get('like'):
            users_liked_image=self.request.user.liked_images.all().filter(pk=self.kwargs['pk'])
            if not users_liked_image:
                UserImage.objects.get(pk=self.kwargs['pk']).popularity.add(self.request.user)
        if self.request.GET.get('unlike'):
            users_liked_image=self.request.user.liked_images.all().filter(pk=self.kwargs['pk'])
            if users_liked_image:
                UserImage.objects.get(pk=self.kwargs['pk']).popularity.remove(self.request.user)

        liked=False
        if self.request.user.liked_images.all().filter(pk=self.kwargs['pk']):
            liked=True
        context['liked']=liked
        return context


class ColourCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Colour
    form_class=ColourForm
    permission_required=("staff")

class ColourPriorityCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Colour_Priority
    form_class=ColourPriorityForm
    permission_required=("staff")

class ColourDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model=Colour
    success_url=reverse_lazy('manage image fields')
    permission_required=("staff")

class ColourPriorityDelete(PermissionRequiredMixin,LoginRequiredMixin,DeleteView):
    model=Colour_Priority
    success_url=reverse_lazy('manage image fields')
    permission_required=("staff")

class Manage_image_fields(PermissionRequiredMixin,LoginRequiredMixin,View):
    permission_required=("staff")
    def get(self, request,*args,**kwargs):
        leagues_nav=None
        colours=Colour.objects.all()
        prioritys=Colour_Priority.objects.all()
        return render(request, 'Gallery/manage_image_fields.html',{"colours":colours,"prioritys":prioritys,"league_nav":leagues_nav,'filter_form':ImageFilter})
