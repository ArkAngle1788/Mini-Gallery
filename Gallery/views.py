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

# from django.conf import settings



class GalleryListView(FilterView):
    model=UserImage
    filterset_class=ImageFilter
    template_name='Gallery/gallery_home.html'
    context_object_name='user_images'
    paginate_by=8

    # def get_queryset(self):
    #
    #
    #     # sort by likes
    #     if self.request.GET.get('recent'):
    #         queryset = super().get_queryset()
    #         queryset=queryset.order_by('-pk')
    #     else:
    #         queryset = super().get_queryset()
    #         queryset=queryset.annotate(num_likes=Count('popularity')).order_by('-num_likes')
    #         # queryset=queryset.order_by('-num_likes')
    #
    #     print(f"\n\n\n\n")
    #     for var in queryset:
    #         print(f"{var.pk}")
    #     print(f"\n\n{self.object_list}\n\n")
    #     return queryset

    # def get_paginator(
    #     self, queryset, per_page, orphans=0, allow_empty_first_page=True, **kwargs
    # ):
    #     """Return an instance of the paginator for this view."""
    #     # print(f"\n\n DEEPEST LEVEL get_paginator quryset at start\n{queryset}\n\n")
    #
    #     # print(f"\n\n!!!!!!!!\n\n")
    #     # for asd in queryset:
    #     #     print(asd.pk)
    #
    #     var=self.paginator_class(queryset,per_page,orphans=orphans,allow_empty_first_page=allow_empty_first_page,**kwargs,)
    #     # print(f"\n\nobject list: \n{var.page(1).object_list}\n\n")
    #     return var

    # def paginate_queryset(self, queryset, page_size):
    #     # print(f"Inside paginate_queryset start of function :\n{queryset}\n")
    #     """Paginate the queryset, if needed."""
    #     paginator = self.get_paginator(
    #         queryset, page_size, orphans=self.get_paginate_orphans(),
    #         allow_empty_first_page=self.get_allow_empty())
    #     page_kwarg = self.page_kwarg
    #     page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
    #
    #     # print(f"\n\nLOOK AT ME: \n\n")
    #     # for prt in paginator.object_list:
    #     #     print(prt.pk)
    #     #
    #     # print(f"paginator meta object list (page1):\n{paginator.page(1).object_list}\n")
    #     # print(f"paginator meta object list (page2):\n{paginator.page(2).object_list}\n")
    #     # print(f"paginator meta object list (page3):\n{paginator.page(3).object_list}\n")
    #     # print(f"paginator meta object list (page4):\n{paginator.page(4).object_list}\n")
    #     # print(f"paginator meta object list (page5):\n{paginator.page(5).object_list}\n")
    #
    #     try:
    #         page_number = int(page)
    #     except ValueError:
    #         if page == 'last':
    #             page_number = paginator.num_pages
    #         else:
    #             raise Http404(_('Page is not “last”, nor can it be converted to an int.'))
    #     try:
    #         page = paginator.page(page_number)
    #         # print(f"\n\nTesting pagination queryset: \n\n")
    #         # for var in queryset:
    #         #     print(var.id)
    #         # print("\ntesting page.object_list\n")
    #         # for var2 in page.object_list:
    #         #     print(var2.id)
    #         return (paginator, page, page.object_list, page.has_other_pages())
    #     except InvalidPage as e:
    #         raise Http404(_('Invalid page (%(page_number)s): %(message)s') % {
    #             'page_number': page_number,
    #             'message': str(e)
    #         })

    def get_context_data(self, *, object_list=None, **kwargs):

        # print(f"class object list inside get_context_data before super call: \n{self.object_list}\n")

        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        #
        # queryset = object_list if object_list is not None else self.object_list
        # page_size = self.get_paginate_by(queryset)
        # context_object_name = self.get_context_object_name(queryset)
        # if page_size:
        #     # print(f"inside super : \n{queryset}\n")
        #     paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
        #     # print(f"inside super after paginate_queryset :\n{queryset}\n")
        #     context = {
        #         'paginator': paginator,
        #         'page_obj': page,
        #         'is_paginated': is_paginated,
        #         'object_list': queryset
        #     }
        # else:
        #     context = {
        #         'paginator': None,
        #         'page_obj': None,
        #         'is_paginated': False,
        #         'object_list': queryset
        #     }
        # if context_object_name is not None:
        #     context[context_object_name] = queryset
        # context.update(kwargs)
        # return super().get_context_data(**context)
        # print("!!!!")
        #
        # print(f"class object list inside get_context_data after super call: \n{self.object_list}\n\n")
        # print(f"object list inside context after super call: \n{context['object_list']}\n")
        # for var in self.object_list:
        #     print(f"{var.pk}")
        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        # context['filter_form']=FilterImages(auto_id="filter_%s")
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter

        if self.request.GET:
            dic_string=dict(self.request.GET)
            if self.request.GET.get('page'):
                dic_string.pop('page')
            context['search']=dic_string

        # print(f"user images before return: \n{context['user_images']}\n\n")
        return context

class GalleryListViewOld(ListView): #defalust objectlist ? object_list? as the context variable
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
        # ordering = self.get_ordering()
        # if ordering:
        #     if isinstance(ordering, str):
        #         ordering = (ordering,)
        #     queryset = queryset.order_by(*ordering)

        print(f"\n\n\n\n")

        for var in queryset:
            print(f"{var.pk}")
        queryset=queryset.order_by('-pk')
        # sort by likes
        if self.request.GET.get('recent'):
            queryset=queryset.order_by('-pk')
        else:
            queryset=queryset.annotate(num_likes=Count('popularity')).order_by('-num_likes')
            # queryset=queryset.order_by('-num_likes')

        # print(f"\n\n\n\n")
        # for var in queryset:
        #     print(f"{var.pk}")

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

        if self.request.GET:
            dic_string=dict(self.request.GET)
            if self.request.GET.get('page'):
                dic_string.pop('page')
            context['search']=dic_string

        return context


class GalleryUpload(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=UserImage
    # fields=['image','image_title','system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','professional','owner']
    form_class=UploadImages
    permission_required=("Gallery.add_userimage")

    # def post(self, request, *args, **kwargs):
    #     var=super().post(self,request,*args,**kwargs)
    #     return var
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



class GalleryUploadMultipart(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=UserImage
    # fields=['image','image_title','system','faction_type','factions','sub_factions','colours','conversion','unit_type','scale','professional','owner']
    form_class=UploadImagesMultipart
    permission_required=("Gallery.add_userimage")
    image_choices=[]

    # def post(self, request, *args, **kwargs):
    #     var=super().post(self,request,*args,**kwargs)
    #     return var
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
        self.image_choices=[]
        form.instance.uploader=self.request.user #add this data first then validate
        object=super().form_valid(form) # then run original form_valid
        files = self.request.FILES.getlist('subimage')


        # for img in files:
        #     subimage=UserSubImage(image=img,image_title=self.object.image_title)
        #     subimage.save()
        #     self.object.sub_image.add(subimage)



        for img in files:
            subimage=TempImage(image=img,uploader=self.request.user)
            subimage.save()
            self.image_choices+=[subimage]
        self.object.image=self.image_choices[0].image
        self.object.save()
        return object
    # def get_success_url(self):
    #
    #     return url
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
        # item_list=','.join(self.image_choices)

        # return render(request, 'Gallery/error.html',{"var":self.image_choices})
        url=reverse('gallery upload multipart confirm')
        url+='?'+f'images={item_list}&main={self.object.pk}'
        return redirect(url)


#GOOGLE_APPLICATION_CREDENTIALS='/etc/solid-ego-284723-ee1d8e55a890.json'

#os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/etc/solid-ego-284723-ee1d8e55a890.json'



class GalleryUploadMultipartConfirm(PermissionRequiredMixin,LoginRequiredMixin,View):

    # form_class=SelectPrimaryImage
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
            # main.sub_image.add(subimage)
            img.image.close()


        imagename_str=get_upload_to()+'/'+os.path.basename(main_image.image.name)
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
        # messages.success(request, f'New League \" {league_name} \" has been created')
        return redirect(url)






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
        # messages.success(request, f'New League \" {league_name} \" has been created')
        return redirect(url)


        # return super().form_valid(form)
    def post(self, request, *args, **kwargs):
        # print(f"\n\npost has run!\n\n")
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        # context['league_nav'] = leagues_nav
        # context['news']=calculate_news_bar()
        context['current_subimages']=UserSubImage.objects.filter(parent_image__pk=self.object.pk)

        # context['image']=self.object
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

    # def delete(self, request, *args, **kwargs):
    #
    #     object=self.get_object()
    #
    #     if object.image:#actually deletes the image file instead of just dereferencing it
    #         image_name=object.image.name
    #         default_storage.delete(image_name)
    #         print("\ndeleting image from delete\n")
    #
    #     return super().delete(self,request,*args,**kwargs)

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
        # context['filter_form']=FilterImages()
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        liked=False
        if self.request.user.is_authenticated:
            if self.request.user.liked_images.all().filter(pk=self.kwargs['pk']):
                liked=True
            context['liked']=liked

        newimage=self.object
        # print(f"testing: {newimage.paintingstudio.all()}")

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
