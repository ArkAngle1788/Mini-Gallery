from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from .models import Conversion, Scale_Of_Image, Colour, Colour_Priority,  Colour_Catagory, UserImage
from ContentPost.custom_functions import calculate_news_bar
from CommunityInfrastructure.models import Country, Region, City, PaintingStudio
from GameData.models import Unit_Type,Faction_Type,Faction,Sub_Faction
from League.models import League

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



class GalleryListView(ListView): #defalust objectlist ? object_list? as the context variable
    template_name='Gallery/gallery_home.html'
    model=UserImage
    context_object_name='user_images'
    # ordering= ['-popularity']
    paginate_by=8 #items per page
    # form_class=FilterImages()

    def get_queryset(self):
        """
        Return the list of items for this view.
        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        if self.queryset is not None:
            queryset = self.queryset
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
            queryset=image_filter.qs
            # queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)

        # sort by likes
        queryset=queryset.annotate(num_likes=Count('popularity')).order_by('-num_likes')

        return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        # context['filter_form']=FilterImages(auto_id="filter_%s")
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter

        return context


class GalleryUpload(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=UserImage
    # fields=['image','image_title','system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','professional','owner']
    form_class=UploadImages
    permission_required=("Gallery.add_userimage")

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        # context['filter_form']=FilterImages()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        return context

    def form_valid(self,form):
        form.instance.uploader=self.request.user #add this data first then validate
        return super().form_valid(form) # then run original form_valid

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
        # context['filter_form']=FilterImages()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        context['multi']=True

        return context

    def get_success_url(self):
        url=super().get_success_url()
        return url+"?images="+self.uploadedimagelist

    def form_valid(self,form):  #a view in CommunityInfrastructure overrides this function. changes here might need to be reflected there as well
        form.instance.uploader=self.request.user #add this data first then validate
        files = self.request.FILES.getlist('image')
        # success_url+="?images="
        # self.object = form.save()
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

        # uploadedimagelist #add the list of images we uploaded to the url so we can edit them
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
        # pklist = self.kwargs.get(self.request.GET('images'))

        if self.request.method == 'POST':
            queryset = queryset.filter(pk=self.request.POST.get('imagepk'))
        if self.request.method == 'GET':
            if not self.request.GET.get('images'):
                raise Http404(f'error: {queryset.model._meta.verbose_name} has not been called correctly')
            pklist=self.request.GET.get('images')
            pklist=pklist.split(',')
            # print(f'\n images from url is : {pklist}\n')
            # print(f'setting object pk to : {pklist[0]}')
            try:
                queryset = queryset.filter(pk=pklist[0])
            except:
                # print("Something went wrong")

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
        # context['filter_form']=FilterImages()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        context['image']=self.object
        if self.request.method=="GET":
            pklist=self.request.GET.get('images')
            pklist=pklist.split(',')
            pklist.pop(0)
            # print(pklist)
            pkliststr=None
            for i in pklist:#we reformat this so that we don't end up with nested list maddness when this gets called multipule times on the same url args
                if not pkliststr:
                    pkliststr=str(i)
                else:
                    pkliststr+=','+str(i)
            context['remaining_images']=pkliststr
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)#this will check that the form is valid

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

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        # context['filter_form']=FilterImages()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        context['image']=self.object
        return context


        # i think this was copied from create? we don't want uploader to change to an admin if and admin edits
    # def form_valid(self,form):
    #     form.instance.uploader=self.request.user #add this data first then validate
    #     return super().form_valid(form) # then run original form_valid

    def test_func(self):
        if self.request.user.is_staff or self.get_object().uploader==self.request.user:
            return True
        return False


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

    def delete(self, request, *args, **kwargs):

        object=self.get_object()

        if object.image:#actually deletes the image file instead of just dereferencing it
            image_name=object.image.name
            default_storage.delete(image_name)
            print("\ndeleting image from delete\n")

        return super().delete(self,request,*args,**kwargs)

    def form_valid(self,form):

        object=self.get_object()

        if object.image:#actually deletes the image file instead of just dereferencing it
            image_name=object.image.name
            default_storage.delete(image_name)
            print("\ndeleting image from form_valid\n")

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
        # context['filter_form']=FilterImages()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        liked=False
        if self.request.user.is_authenticated:
            if self.request.user.liked_images.all().filter(pk=self.kwargs['pk']):
                liked=True
            context['liked']=liked

        newimage=self.object
        print(f"testing: {newimage.paintingstudio.all()}")

        return context

class GalleryDetailUpvoteView(DetailView): #default objectlist ? object_list? as the context variable
    # template_name='Gallery/gallery_home.html'
    model=UserImage
    context_object_name='image'


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        # context['filter_form']=FilterImages()
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

        print(UserImage.objects.get(pk=self.kwargs['pk']).popularity.all())
        print(self.request.user.liked_images.all())
        # print(users_liked_image)
        print(self.kwargs['pk'])

        liked=False
        if self.request.user.liked_images.all().filter(pk=self.kwargs['pk']):
            liked=True
        context['liked']=liked
        return context



class ColourCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Colour
    # fields=['colour_name']
    form_class=ColourForm
    # template_name='Gallery/image_field_form.html'
    permission_required=("staff")



class ColourPriorityCreate(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Colour_Priority
    form_class=ColourPriorityForm
    # fields='__all__'
    # template_name='Gallery/image_field_form.html'
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
