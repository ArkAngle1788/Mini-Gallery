from django.shortcuts import render,redirect#, get_object_or_404

from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.contrib.auth.models import Group as PermGroup
from django.contrib import messages
from django.http import Http404
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from CommunityInfrastructure.models import Country, Region, City, PaintingStudio
from CommunityInfrastructure.models import Group as CIgroup  #Think we had a keyword collision here where group is our model but also a model used for permissions in django authentication
from .forms import *
from ContentPost.custom_functions import calculate_news_bar

from UserAccounts.models import UserProfile,AdminProfile
from Gallery.models import UserImage
from django.db.models import Count, Q
from Gallery.filters import ImageFilter

import requests
import json
import urllib.parse
from allauth.socialaccount.models import SocialToken,SocialAccount

# from Gallery.models import Professional
# from ContentPost.models import ContentPost



# leagues_nav=League.objects.filter(child_season__current_season__isnull=False)
#
# def calculate_news_bar():
#     news_all=ContentPost.objects.all().order_by('-headline','-date_posted')
#
#     #this seems like a terrible way to take the first 5 enteries but here we are
#     news=[]
#     if news_all:
#         news+=[news_all.first()]
#         news_all=news_all.exclude(id=news_all.first().id)
#     if news_all:
#         news+=[news_all.first()]
#         news_all=news_all.exclude(id=news_all.first().id)
#     if news_all:
#         news+=[news_all.first()]
#         news_all=news_all.exclude(id=news_all.first().id)
#     if news_all:
#         news+=[news_all.first()]
#         news_all=news_all.exclude(id=news_all.first().id)
#     if news_all:
#         news+=[news_all.first()]
#         news_all=news_all.exclude(id=news_all.first().id)
#     return news



def home(request):
    return render(request,'CommunityInfrastructure/home.html',{'news':calculate_news_bar()})


def about(request):

    return render(request, 'CommunityInfrastructure/about.html',{'news':calculate_news_bar()})

def contact(request):
    return render(request,'CommunityInfrastructure/contact.html',{'news':calculate_news_bar()})




class Groups_top(ListView):
    model=CIgroup
    context_object_name='groups'
    ordering=['-group_name']
    paginate_by=10



    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the Country QuerySet
        context['zone_container'] = Country.objects.all()
        context['studio_container']=PaintingStudio.objects.all()


        return context
    def get(self, request,*args,**kwargs):

        return super().get(self, request,*args,**kwargs)


# path('<str:league>/', Group.as_view(), name='Group info'),

class Groups_by_zone(ListView):
    model=CIgroup
    context_object_name='groups'
    ordering=['-group_name']
    # paginate_by=2 #can't do this b/c of how i'm currently defining context data but it should be possible somehow


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in the zone QuerySet
        # check to see if null to determine which zone type to use

        zone=self.kwargs['zone']
        context['currentzonestr']=zone#sending this so we can easily display what zone we're in on the page





        # check for city
        # sidebar for city level should show different content
        contextregionzone = City.objects.filter(city_name=zone)
        contextcitygroup = CIgroup.objects.filter(location_city__city_name=zone)
        if contextregionzone:
            context['groups']=contextcitygroup
            context['studio_container']=PaintingStudio.objects.filter(location__city_name=zone)
            context['previouszone']=contextregionzone[0].region#Get a location to build a back link
            context['citylevel']=True#this flag is so that we don't display the no regions added label on the sidebar while viewing cities
            return context


        # check for region
        contextregionzone = City.objects.filter(region__region_name=zone)#contextregionzone holds all the zones in a region (cities)
        contextregiongroup = CIgroup.objects.filter(location_region__region_name=zone)
        if contextregionzone or contextregiongroup:
            context['zone_container']=contextregionzone
            context['groups']=contextregiongroup
            context['studio_container']=PaintingStudio.objects.filter(location__region=Region.objects.get(region_name=zone))#something about the string compare made this not work so we need to call the region object directly
            context['groups_in_subzone']=CIgroup.objects.filter(location_city__region__region_name=zone)
            context['previouszone']=Region.objects.get(region_name=zone).country#Get a location to build a back link
            return context

        # check for country
        contextcountryzone = Region.objects.filter(country__country_name=zone)
        contextcountrygroup = CIgroup.objects.filter(location_country__country_name=zone)
        if contextcountryzone:
            context['zone_container']=contextcountryzone
            context['groups']=contextcountrygroup
            context['studio_container']=PaintingStudio.objects.filter(location__region__country=Country.objects.get(country_name=zone))#see region check note
            context['groups_in_subzone']=CIgroup.objects.filter(Q(location_region__country__country_name=zone)|Q(location_city__region__country__country_name=zone))
            return context

        # messages.error(self.request, 'Something is wrong please tell an admin')#jk there's just no groups for the zone  -- can happen when we add zones for gallery that don't have groups associated with them

        context['groups']=[]
        return context



class Group(DetailView):
    model=CIgroup
    context_object_name='group'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        zone=self.kwargs['zone']
        context['currentzonestr']=zone

        return context

# we use UserPassesTestMixin here because since you can admin multipule leagues that is not a helpful tag here
class Group_add_admin(LoginRequiredMixin,UserPassesTestMixin,View): #remove uses basically the same function so if there are any structural changes here they should happen  to remove as well

    def test_func(self):#this checks to see if you're allowed to use this functionality

        group=CIgroup.objects.get(pk=self.kwargs['pk'])

        if self.request.user.is_staff:
            return True

        # only primary admins can add new admins
        for admin in group.group_primary_admins.all():
            # print(admin)
            # print(' matches ')
            # print(self.request.user.profile)
            if admin.userprofile == self.request.user.profile:
                return True

        return False


    # this is to select the admin to add
    def get(self, request,*args,**kwargs):

        group=CIgroup.objects.get(pk=self.kwargs['pk'])


        # should we be using UserAccounts here or User?

        # local_members=None


        if group.location_city:
            local_members_primary=UserProfile.objects.filter(location=group.location_city)
        elif group.location_region:
            local_members_primary=UserProfile.objects.filter(location__region=group.location_region)
        elif group.location_country:
            local_members_primary=UserProfile.objects.filter(location__region__country=group.location_country)
        else:
            render(request, 'error.html')



        print(group.group_primary_admins.all())
        # exclude existing primary admins (existing secondary admins are left in b/c you can be promoted)
        for adminprofile in group.group_primary_admins.all():#iterates through local members and excludes all admins
            local_members_primary=local_members_primary.exclude(id=adminprofile.userprofile.id)



        # we duplicate after the first exclude b/c we don't want any primary admins showing up in selection for secondary ones
        local_members_secondary=local_members_primary

        # exclude existing (primary and secondary) admins for secondary
        for adminprofile in group.group_secondary_admins.all():#iterates through local members and excludes all admins
            local_members_secondary=local_members_secondary.exclude(id=adminprofile.userprofile.id)



        return render(request, 'CommunityInfrastructure/group_add_admin.html',{'group':group,'local_members_primary':local_members_primary,'local_members_secondary':local_members_secondary})


    # this is to apply the selection
    def post(self, request,*args,**kwargs):

        group=CIgroup.objects.get(pk=self.kwargs['pk'])
        selected_primary_admins_pk=self.request.POST.getlist('select admins primary')
        selected_secondary_admins_pk=self.request.POST.getlist('select admins secondary')

        for admin_pk in selected_primary_admins_pk:
            admin_userprofile=UserProfile.objects.get(id=admin_pk)
            print(admin_userprofile)
            if hasattr(admin_userprofile, 'linked_admin_profile'):
                # print("save new managment")

                admin_userprofile.linked_admin_profile.groups_managed_primary.add(group)
                prim_admin_group = PermGroup.objects.get(name='Primary Group Admin')
                admin_userprofile.user.groups.add(prim_admin_group)

                # if a user was already a secondary admin we remove them from that tier and promote them
                if admin_userprofile.linked_admin_profile.groups_managed_secondary.filter(id=group.id):
                    admin_userprofile.linked_admin_profile.groups_managed_secondary.remove(group)
                    if not admin_userprofile.linked_admin_profile.groups_managed_secondary.all():
                        sec_admin_group = PermGroup.objects.get(name='Secondary Group Admin')
                        admin_userprofile.user.groups.remove(sec_admin_group)

                # also check to see if we need to remove existing secondary status

            # userprofile
            # groups_managed_primary
            # groups_managed_secondary
            # leagues_managed

                # save_me_L=League(league_name=league_name, system=game,league_description=request.POST.get('league description'))
                #         save_me_L.save()
            else:#we don't need double submission check here since if it is double submitted the above if will catch it



                # make a new AdminProfile
                new_profile=AdminProfile(userprofile=admin_userprofile)
                new_profile.save()
                new_profile.groups_managed_primary.add(group)

                prim_admin_group = PermGroup.objects.get(name='Primary Group Admin')

                # either method here works to add the group to the user
                # prim_admin_group.user_set.add(admin_userprofile.user)
                admin_userprofile.user.groups.add(prim_admin_group)

                # if request.user.groups.filter(name="group_name").exists():

                # print("create new linked_admin_profile")


        for admin_pk in selected_secondary_admins_pk:
            admin_userprofile=UserProfile.objects.get(id=admin_pk)
            print(admin_userprofile)
            if hasattr(admin_userprofile, 'linked_admin_profile'):
                # print("save new managment")

                admin_userprofile.linked_admin_profile.groups_managed_secondary.add(group)
                sec_admin_group = PermGroup.objects.get(name='Secondary Group Admin')
                admin_userprofile.user.groups.add(sec_admin_group)

                # think we just don't need this kind of check for secondary since you can't even select an admin for this if they're a primary
                # if admin_userprofile.linked_admin_profile.groups_managed_secondary.filter(id=group.id):
                #     admin_userprofile.linked_admin_profile.groups_managed_secondary.remove(group=group)
                #     if not admin_userprofile.linked_admin_profile.groups_managed_secondary.all():
                #         sec_admin_group = PermGroup.objects.get(name='Secondary Group Admin')
                #         admin_userprofile.user.groups.remove(sec_admin_group)

                # also check to see if we need to remove existing secondary status

            # userprofile
            # groups_managed_primary
            # groups_managed_secondary
            # leagues_managed

                # save_me_L=League(league_name=league_name, system=game,league_description=request.POST.get('league description'))
                #         save_me_L.save()
            else:#we don't need double submission check here since if it is double submitted the above if will catch it



                # make a new AdminProfile
                new_profile=AdminProfile(userprofile=admin_userprofile)
                new_profile.save()
                new_profile.groups_managed_secondary.add(group)

                sec_admin_group = PermGroup.objects.get(name='Secondary Group Admin')

                # either method here works to add the group to the user
                # prim_admin_group.user_set.add(admin_userprofile.user)
                admin_userprofile.user.groups.add(sec_admin_group)

                # if request.user.groups.filter(name="group_name").exists():

                # print("create new linked_admin_profile")







        # return redirect('group add admin' group.location_city group.slug group.id)
        url=reverse('groups top')
        url+=f'/{group.location_country}/{group.slug()}/{group.id}'
        return redirect(url)


class Group_remove_admin(LoginRequiredMixin,UserPassesTestMixin,View):

    def test_func(self):#this checks to see if you're allowed to use this functionality

        group=CIgroup.objects.get(pk=self.kwargs['pk'])

        if self.request.user.is_staff:
            return True

        # only primary admins can remove admins
        for admin in group.group_primary_admins.all():
            if admin.userprofile == self.request.user.profile:
                return True

        return False


    # this is to select the admin to remove
    def get(self, request,*args,**kwargs):

        group=CIgroup.objects.get(pk=self.kwargs['pk'])

        # note: this is selecting AdminProfile instead of user so we need to account for that in the html
        admins_primary=group.group_primary_admins.all()
        admins_secondary=group.group_secondary_admins.all()


        return render(request, 'CommunityInfrastructure/group_remove_admin.html',{'group':group,'admins_primary':admins_primary,'admins_secondary':admins_secondary})


    # this is to apply the selection
    def post(self, request,*args,**kwargs):

        group=CIgroup.objects.get(pk=self.kwargs['pk'])
        remove_primary_admins_pk=self.request.POST.getlist('remove admins primary')
        remove_secondary_admins_pk=self.request.POST.getlist('remove admins secondary')

        for admin_pk in remove_primary_admins_pk:
            admin_userprofile=UserProfile.objects.get(id=admin_pk)
            if hasattr(admin_userprofile, 'linked_admin_profile'):

                admin_userprofile.linked_admin_profile.groups_managed_primary.remove(group)


                # if a user has no more primary admin roles left we need to remove the role
                if not admin_userprofile.linked_admin_profile.groups_managed_primary.all():
                    prim_admin_group = PermGroup.objects.get(name='Primary Group Admin')
                    admin_userprofile.user.groups.remove(prim_admin_group)


            else:#an admin profile should always exist to get this far
                render(request, 'error.html')




        for admin_pk in remove_secondary_admins_pk:
            admin_userprofile=UserProfile.objects.get(id=admin_pk)

            if hasattr(admin_userprofile, 'linked_admin_profile'):
                admin_userprofile.linked_admin_profile.groups_managed_secondary.remove(group)

                # if a user has no more secondary admin roles left we need to remove the role
                if not admin_userprofile.linked_admin_profile.groups_managed_secondary.all():
                    sec_admin_group = PermGroup.objects.get(name='Secondary Group Admin')
                    admin_userprofile.user.groups.remove(sec_admin_group)


            else:#an admin profile should always exist to get this far
                render(request, 'error.html')

        # return redirect('group add admin' group.location_city group.slug group.id)
        url=reverse('groups top')
        url+=f'/{group.location_country}/{group.slug()}/{group.id}'
        return redirect(url)


class Group_Create(LoginRequiredMixin,UserPassesTestMixin,CreateView):  #shares a template with update view -- <model>_form.html
    model=CIgroup
    # fields=['group_name','group_tag','group_description','location_city','location_region','location_country']
    form_class = Group_Form


    def form_valid(self,form):
        form.instance.uploader=self.request.user #add this data first then validate

        if form.instance.location_city:
            if form.instance.location_region or form.instance.location_country:
                return super().form_invalid(form)

        return super().form_valid(form) # then run original form_valid


    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

class Group_Delete(LoginRequiredMixin,UserPassesTestMixin,DeleteView):
    model=CIgroup
    success_url=reverse_lazy('groups top')
    context_object_name='group'

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False

    def delete(self, request, *args, **kwargs):
        group=self.get_object()

        group_primary_admins=group.group_primary_admins.all()
        group_secondary_admins=group.group_secondary_admins.all()


        for admin in group_primary_admins:
            admin.groups_managed_primary.remove(group)
            # if the list is now empty they also need their permissions removed
            if not admin.groups_managed_primary.all():
                prim_admin_group = PermGroup.objects.get(name='Primary Group Admin')
                admin.userprofile.user.groups.remove(prim_admin_group)
        for admin in group_secondary_admins:
            admin.groups_managed_secondary.remove(group)
            # if the list is now empty they also need their permissions removed
            if not admin.groups_managed_secondary.all():
                sec_admin_group = PermGroup.objects.get(name='Secondary Group Admin')
                admin.userprofile.user.groups.remove(sec_admin_group)



        # I think leagues will automatically delete themselves when the league is deleated?

        # remove privlages from existing admins

        return super().delete(self,request,*args,**kwargs)

class Studio_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):  #shares a template with update view -- <model>_form.html
    model=PaintingStudio
    # fields='__all__'
    form_class = Studio_Form
    permission_required = ('staff')

class Studio_Edit(LoginRequiredMixin,UserPassesTestMixin,UpdateView):  #shares a template with update view -- <model>_form.html
    model=PaintingStudio
    # fields='__all__'
    form_class = Studio_Form
    # permission_required = ('staff')

    def test_func(self):#this checks to see if you're allowed to use this functionality

        if self.request.user.is_staff or self.request.user==self.object.userprofile:
            return True


        return False

class Studio_Details(ListView):
    model=UserImage
    context_object_name='studio_images'
    paginate_by=8
    template_name='CommunityInfrastructure/paintingstudio_detail.html'

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
                # studio_uploader=PaintingStudio.objects.get(pk=self.kwargs['pk']).userprofile
                # queryset=UserImage.objects.filter(uploader=studio_uploader).annotate(num_likes=Count('popularity')).order_by('-num_likes')
                queryset=PaintingStudio.objects.get(pk=self.kwargs['pk']).studios_images.all().filter(studio_images__official=True).order_by('-pk')#show the most recent images first


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

            return queryset

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        # context['filter_form']=FilterImages(auto_id="filter_%s")
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        context['studio']=PaintingStudio.objects.get(pk=self.kwargs['pk'])
        context['form']=SelectExport()


        contextregionzone = City.objects.filter(region__region_name=PaintingStudio.objects.get(pk=self.kwargs['pk']).location.region)
        if contextregionzone:
            context['zone_container']=contextregionzone
            return context

        return context

from Gallery.views import GalleryMultipleUpload
import django.dispatch
new_studio_image = django.dispatch.Signal()
from django.views.generic.edit import FormMixin
class Studio_Upload(UserPassesTestMixin,GalleryMultipleUpload):
    def test_func(self):
        if self.request.user.is_staff or self.request.user==PaintingStudio.objects.get(pk=self.kwargs['pk']).userprofile:
            return True
        return False

    def form_valid(self,form): #this is almost identical to GalleryMultipleUpload's code but we need to send a signal in the middle
        form.instance.uploader=self.request.user #add this data first then validate
        files = self.request.FILES.getlist('image')
        for f in files:

            form.instance.image=f

            newimage=form.save(commit=False)
            # print(f'NI starts as {newimage.id}')

            newimage.pk=None
            newimage.save()
            form.save_m2m()
            studio=PaintingStudio.objects.get(pk=self.kwargs['pk'])#still not really sure why this has to be on its own line

            try:
                newimage.paintingstudio.get(id=studio.id)
            except:
                newimage.paintingstudio.add(studio)

            new_studio_image.send(sender=self.__class__, image=newimage, studio=studio)


            if self.uploadedimagelist == '' :
                self.uploadedimagelist+=str(newimage.pk)
            else:
                self.uploadedimagelist+=','
                self.uploadedimagelist+=str(newimage.pk)


        self.object=newimage#this stayed here b/c the createview class needs an object to bind to but it doesn't matter which one b/c we've changed functionality so much

        # uploadedimagelist #add the list of images we uploaded to the url so we can edit them
        return FormMixin.form_valid(self,form) # then run original form_valid




class Studio_Export(LoginRequiredMixin,UserPassesTestMixin,View):#when we have selected which platform to use we come here to begin initial configuration

    def test_func(self):#this checks to see if you're allowed to use this functionality


        if self.request.user.is_staff or self.request.user==PaintingStudio.objects.get(pk=self.kwargs['pk']).userprofile:
            return True


        return False

    def get(self,request,*args,**kwargs):

        return render(request, 'error.html')

    def post(self, request,*args,**kwargs):

        if self.request.POST.get('platform')=="Facebook":#for facebook exports we first need to configure the account since facebook logins are used as well on the site.

            studio=PaintingStudio.objects.get(pk=self.kwargs['pk'])
            owner=studio.userprofile
            # tokens and user id's should already exist because of facebook login/permission escalation being step one

#     -------------->   if you bypass by intercepting traffic tokenobject could be null      <-----------------------------------------------------------
                    # it can also be null if you haven't linked a facebook account at all
            try: tokenobject=SocialToken.objects.get(account__user=owner)#account is a socialaccount model
            except:
                messages.error(request, 'you must add a facebook account before you can use this feature')
                return redirect('/accounts/social/connections/')
                # raise Http404(f'error: A Social Account is not properly configured')

            userid=SocialAccount.objects.get(user=owner).uid
            apiurlstring='https://graph.facebook.com/v13.0/'+userid+'/accounts?access_token='+tokenobject.token+''#fetch the pages a user is authorized to upload to
            # print(apiurlstring)

            response = requests.get(apiurlstring)#call the facebook api
            responsejson=response.json()
            if 'error' in responsejson:
                raise Http404(f'{responsejson}')

            pages_managed=[]
            for page in responsejson["data"]:
                var={'name':page['name'],'id':page['id']}
                pages_managed=pages_managed+[var]

            count=self.request.POST.get('select_number')


            return render(request, 'CommunityInfrastructure/export_select_facebook.html',{'pages_managed':pages_managed,'count':count,'studio':studio})

        if self.request.POST.get('platform')=="Instagram":#for instagram exports we first need to configure the account since it uses facebook api and facebook logins are used as well on the site.

            studio=PaintingStudio.objects.get(pk=self.kwargs['pk'])
            owner=studio.userprofile
            # tokens and user id's should already exist because of facebook login/permission escalation being step one

#     -------------->   if you bypass by intercepting traffic tokenobject could be null      <-----------------------------------------------------------
                    # it can also be null if you haven't linked a facebook account at all
            try: tokenobject=SocialToken.objects.get(account__user=owner)#account is a socialaccount model
            except:
                messages.error(request, 'you must add a facebook account before you can use this feature')
                return redirect('/accounts/social/connections/')
                # raise Http404(f'error: A Social Account is not properly configured')

            userid=SocialAccount.objects.get(user=owner).uid
            apiurlstring='https://graph.facebook.com/v13.0/'+userid+'/accounts?access_token='+tokenobject.token+''#fetch the pages a user is authorized to upload to
            # print(apiurlstring)

            response = requests.get(apiurlstring)#call the facebook api
            responsejson=response.json()

            if 'error' in responsejson:
                raise Http404(f'{responsejson}')


            pages_managed=[]
            for page in responsejson["data"]:
                var={'name':page['name'],'id':page['id']}
                pages_managed=pages_managed+[var]

            count=self.request.POST.get('select_number')


            return render(request, 'CommunityInfrastructure/export_select_instagram.html',{'pages_managed':pages_managed,'count':count,'studio':studio})

        return render(request, 'error.html')

class Studio_Request_Facebook(LoginRequiredMixin,UserPassesTestMixin,View): #continue the process of a facebook image upload by selecting the album or if that has already been done upload the images

    def test_func(self):
        if self.request.user.is_staff or self.request.user==PaintingStudio.objects.get(pk=self.kwargs['pk']).userprofile:
            return True
        return False

    # def get(self,request,*args,**kwargs):
    #
    #     return render(request, 'CommunityInfrastructure/export.html',{'test':test})

    def post(self, request,*args,**kwargs):

        studio=PaintingStudio.objects.get(pk=self.kwargs['pk'])
        owner=studio.userprofile
        tokenobject=SocialToken.objects.get(account__user=owner)#account is a socialaccount model



        if self.request.POST.get('select_album'):
            albumid=self.request.POST.get('select_album')#if albumid is maliciously set it will just cause the facebook api call to fail. Entering this check early by artificially adding the parameter looks like it can be handled by the api fail error state
            try:
                count=int(self.request.POST.get('count'))
            except:
                raise Http404(f'error: {count} has not been called correctly you hacker')
            #we replicate the way images are displayed on the studio page for consistant uploading selection
            studio_uploader=PaintingStudio.objects.get(pk=self.kwargs['pk']).userprofile
            # studios_images=UserImage.objects.filter(uploader=studio_uploader).annotate(num_likes=Count('popularity')).order_by('-num_likes')#this misses out on the offical flag
            studios_images=PaintingStudio.objects.get(pk=studio.pk).studios_images.all().filter(studio_images__official=True).order_by('-pk')


            #now that we have all the information we need to call the api to get the page access token
            userid=SocialAccount.objects.get(user=owner).uid
            # this can probably be cleaned up into one call if we care
            apiurlstringforpage='https://graph.facebook.com/v13.0/'+userid+'/accounts?access_token='+tokenobject.token
            pages = requests.get(apiurlstringforpage).json()
            if 'error' in pages:
                raise Http404(f'{pages}')
            # there might be multipule pages available
            pagetoken=''
            for page in pages['data']:
                if page['id']==self.request.POST.get('page_id'):
                    pagetoken=page['access_token']

            if not pagetoken:
                raise Http404(f'error: unable to resolve page access')

            if not count<=10 or not count>=1:
                raise Http404(f'error: {count} has not been called correctly you hacker')

            # now that we have the page token we can upload the images
            for i in range(count):
                description=studios_images[i].image_title
                imageurl=studios_images[i].image.url
                apiurlstring='https://graph.facebook.com/v13.0/'+albumid+'/photos?caption='+description+'&url='+imageurl+'&access_token='+pagetoken
                # print(apiurlstring)
                responsejson = requests.post(apiurlstring).json()
                if responsejson['error']:
                    # raise Http404(f'{responsejson}')
                    return render(request, 'error.html',{'error':f'{responsejson}'})
            test=responsejson
            return render(request, 'CommunityInfrastructure/exportcomplete.html',{'test':test})

        if self.request.POST.get('select_page'):#here we take the page id and find available albums to post in. an improperly named select_page will simply cause the api lookup to fail

            pageid=self.request.POST.get('select_page')
            apiurlstring='https://graph.facebook.com/v13.0/'+pageid+'/albums?access_token='+tokenobject.token
            # print(apiurlstring)

            responsejson = requests.get(apiurlstring).json()
            if 'error' in responsejson:
                raise Http404(f'{responsejson}')
            # print(responsejson)

            # get a list of albums
            albums=[]
            for album in responsejson["data"]:
                var={'name':album['name'],'id':album['id']}
                albums=albums+[var]
            test='placeholder'
            test2=tokenobject
            count=self.request.POST.get('count')#still need this in the future will confirm it hasn't been tampered with later

            return render(request, 'CommunityInfrastructure/exportfacebook.html',{'test':test,'test2':test2,'albums':albums,'page_id':pageid,'count':count,'studio':studio})


        raise Http404(f'post error')

class Studio_Request_Instagram(LoginRequiredMixin,UserPassesTestMixin,View): #continue the process of a facebook image upload by selecting the album or if that has already been done upload the images

    def test_func(self):
        if self.request.user.is_staff or self.request.user==PaintingStudio.objects.get(pk=self.kwargs['pk']).userprofile:
            return True
        return False

    def post(self, request,*args,**kwargs):

        studio=PaintingStudio.objects.get(pk=self.kwargs['pk'])
        owner=studio.userprofile
        tokenobject=SocialToken.objects.get(account__user=owner)#account is a socialaccount model

        if self.request.POST.get('select_page'):#here we take the page id and find available albums to post in. an improperly named select_page will simply cause the api lookup to fail

            pageid=self.request.POST.get('select_page')
            caption=self.request.POST.get('caption')
            carousel_id=None
            try:
                count=int(self.request.POST.get('count'))
            except:
                raise Http404(f'error: {count} has not been called correctly you hacker')

            apiurlstring='https://graph.facebook.com/v13.0/'+pageid+'?fields=instagram_business_account&access_token='+tokenobject.token

            if not count<=10 or not count>=1:
                raise Http404('not this time')

            # call the API to get the instagram_business_account
            responsejson = requests.get(apiurlstring).json()
            if 'error' in responsejson:
                messages.error(request, 'The request returned and error. Make sure you have enabled the appropriate permissions')
                raise redirect(request.META['HTTP_REFERER'])

            if not ('instagram_business_account' in responsejson):
                raise Http404(f'Misconfigured Response (this can happen if your permissions are not set up properly): {responsejson}')
            igid=responsejson["instagram_business_account"]['id']

            if count == 1:
                studio_image_set=PaintingStudio.objects.get(pk=studio.pk).studios_images.all().filter(studio_images__official=True).order_by('-pk')
                image_url=studio_image_set[0].image.url
                apiurlstring2='https://graph.facebook.com/v13.0/'+igid+'/media?image_url='+image_url+'&access_token='+tokenobject.token
                if not caption == '':
                    apiurlstring2+=('&caption='+urllib.parse.quote(caption))
                #call the API
                responsejson2 = requests.post(apiurlstring2).json()
                if 'error' in responsejson2:
                    raise Http404(f'initial upload error: \n{apiurlstring2}\n{responsejson2}')
                if not ('id' in responsejson2):
                    raise Http404(f'Misconfigured Response: {responsejson2}')
                # print(f"\n\nresponse was: {responsejson2}\n\n")
                image_post_id=responsejson2['id']

                apiurlstring3='https://graph.facebook.com/v13.0/'+igid+'/media_publish?creation_id='+image_post_id+'&access_token='+tokenobject.token
                #call the API
                responsejson3 = requests.post(apiurlstring3).json()
                if 'error' in responsejson3:
                    raise Http404(f'publish error: {responsejson3}')

            else:
                image_post_id_list=[]
                for i in range(count):

                    studio_image_set=PaintingStudio.objects.get(pk=studio.pk).studios_images.all().filter(studio_images__official=True).order_by('-pk')#ordered with most recent first
                    image_url=studio_image_set[i].image.url
                    apiurlstring2='https://graph.facebook.com/v13.0/'+igid+'/media?image_url='+image_url+'&is_carousel_item=true&access_token='+tokenobject.token

                    #call the API
                    responsejson2 = requests.post(apiurlstring2).json()
                    if 'error' in responsejson2:
                        raise Http404(f'misconfigured image upload request: \n{apiurlstring2}\n{responsejson2}')
                    if not ('id' in responsejson2):
                        raise Http404(f'Misconfigured Response: {responsejson2}')
                    print(f"\n\nresponse (image upload) was: {responsejson2}\n\n")
                    image_post_id_list+=[responsejson2['id']]


                apiurlstring3='https://graph.facebook.com/v13.0/'+igid+'/media?media_type=CAROUSEL&access_token='+tokenobject.token+'&children='
                first=True
                children=''
                for i in image_post_id_list:
                    if first:
                        children+=i
                        first=False
                    else:
                        children+=','+i

                children=urllib.parse.quote(children)#documentation leaves this part out but the list is supposed to be url encoded commas
                apiurlstring3+=children
                if not caption == '':
                    apiurlstring3+=('&caption='+urllib.parse.quote(caption))#this will encode everything not just the # that the docs specifically call for
                #call the API
                responsejson3 = requests.post(apiurlstring3).json()
                if 'error' in responsejson3:
                    raise Http404(f'misconfigured carousel creation request: \n{apiurlstring3}\n{responsejson3}')
                if not ('id' in responsejson3):
                    raise Http404(f'Misconfigured Response: {responsejson3}')
                carousel_id=responsejson3['id']


                apiurlstring4='https://graph.facebook.com/v13.0/'+igid+'/media_publish?creation_id='+carousel_id+'&access_token='+tokenobject.token
                #call the API
                responsejson4 = requests.post(apiurlstring4).json()
                if 'error' in responsejson4:
                    raise Http404(f'publish error: {responsejson4}')


            # this gets a list of our instagram posts
            apiurlstring2='https://graph.facebook.com/v13.0/'+igid+'/media?access_token='+tokenobject.token
            responsejson2 = requests.get(apiurlstring2).json()
            print(responsejson2)
            test=responsejson2
            test2=f'c_id is: {carousel_id}'
            albums=None



            return render(request, 'CommunityInfrastructure/exportcomplete.html',{'test':test,'test2':test2,'albums':albums,'page_id':pageid,'count':count,'studio':studio})

        raise Http404(f'post error')

class Country_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Country
    # fields='__all__'
    form_class=Country_Form
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_country')

class Region_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=Region
    # fields='__all__'
    form_class = Region_Form
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_region')

class City_Create(PermissionRequiredMixin,LoginRequiredMixin,CreateView):
    model=City
    # fields='__all__'
    form_class = City_Form
    template_name='GameData/game_data_form.html'
    permission_required = ('GameData.add_city')
