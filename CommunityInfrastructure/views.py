import urllib.parse

import requests
from allauth.socialaccount.models import SocialAccount, SocialToken
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin,
                                        UserPassesTestMixin)
from django.contrib.auth.models import Group as PermGroup
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.db.models import Q, QuerySet
from django.http import Http404
from django.shortcuts import redirect, render  # , get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)
# from django.views.generic.edit import FormMixin
from django_filters.views import FilterView

from CommunityInfrastructure.models import City, Country
from CommunityInfrastructure.models import Group as CIgroup
from CommunityInfrastructure.models import PaintingStudio, Region
from ContentPost.custom_functions import calculate_news_bar
from Gallery.filters import ImageFilter
from Gallery.models import UserImage
from Gallery.views import GalleryMultipleUpload, GalleryUploadMultipart
from UserAccounts.models import AdminProfile, UserProfile

from .custom_functions import studio_admin_check
from .forms import (ApproveUserForm, CityForm, CountryForm, GroupForm,
                    RegionForm, SelectExport, StudioForm)


def home(request):
    """Displays the site landing page"""

    return render(request, 'CommunityInfrastructure/home.html', {'news': calculate_news_bar()})


def about(request):
    """Explains website, currently static html. Could be upgraded to be editable through site."""
    return render(request, 'CommunityInfrastructure/about.html', {'news': calculate_news_bar()})


def contact(request):
    """static contact html page"""
    return render(request, 'CommunityInfrastructure/contact.html', {'news': calculate_news_bar()})


def privacy_policy(request):
    """generated using external site, required by facebook login and API"""
    return render(request, 'CommunityInfrastructure/privacy_policy.html')


class GroupsTop(ListView):
    """Top level display of all groups that exist. Also displays commission painters"""
    model = CIgroup
    context_object_name = 'groups'
    ordering = ['-group_name']
    paginate_by = 10

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the addional QuerySets
        context['zone_container'] = Country.objects.all()
        context['studio_container'] = PaintingStudio.objects.all()
        return context


class GroupsByZone(ListView):
    """
    Displays groups selected from GroupsTop according to the zone qualifier,
    can be a country/region/city
    """
    model = CIgroup
    context_object_name = 'groups'
    ordering = ['-group_name']

    # do we want pagination? we would need to update the logic on context_data if so

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in the zone QuerySet
        # check to see if null to determine which zone type to use

        zone = self.kwargs['zone']
        # sending this so we can easily display what zone we're in on the page
        context['currentzonestr'] = zone

        # check for city
        contextregionzone = City.objects.filter(city_name=zone)
        contextcitygroup = CIgroup.objects.filter(
            location_city__city_name=zone)
        if contextregionzone:
            context['groups'] = contextcitygroup
            context['studio_container'] = PaintingStudio.objects.filter(
                location__city_name=zone)
            # Get a location to build a back link
            context['previouszone'] = contextregionzone[0].region
            # this flag is so that we don't display the no regions added
            # label on the sidebar while viewing cities
            context['citylevel'] = True
            return context

        # check for region
        contextregionzone = City.objects.filter(
            region__region_name=zone)  # contextregionzone holds all the zones in a region (cities)
        contextregiongroup = CIgroup.objects.filter(
            location_region__region_name=zone)
        if contextregionzone or contextregiongroup:
            context['zone_container'] = contextregionzone
            context['groups'] = contextregiongroup
            context['studio_container'] = PaintingStudio.objects.filter(
                location__region=Region.objects.get(region_name=zone))
            context['groups_in_subzone'] = CIgroup.objects.filter(
                location_city__region__region_name=zone)
            context['previouszone'] = Region.objects.get(
                region_name=zone).country  # Get a location to build a back link
            return context

        # check for country
        contextcountryzone = Region.objects.filter(country__country_name=zone)
        contextcountrygroup = CIgroup.objects.filter(
            location_country__country_name=zone)
        if contextcountryzone:
            context['zone_container'] = contextcountryzone
            context['groups'] = contextcountrygroup
            context['studio_container'] = PaintingStudio.objects.filter(
                location__region__country=Country.objects.get(
                    country_name=zone))
            context['groups_in_subzone'] = CIgroup.objects.filter(
                Q(location_region__country__country_name=zone)
                | Q(location_city__region__country__country_name=zone))
            return context

        # if we get here there's just no groups for the zone
        # this can happen when we add zones for the gallery or user profiles
        # that don't have groups associated with them

        context['groups'] = []
        return context


class Group(DetailView):
    """displays group details, sidebar will show leagues"""
    model = CIgroup
    context_object_name = 'group'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        zone = self.kwargs['zone']
        context['currentzonestr'] = zone
        return context


class GroupAddAdmin(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    allows admin or staff to add administrator to their groups.
    Add and remove admin share a lot of code that could be combined,
    this has been added to the todo list
    """

    def test_func(self):  # this checks to see if you're allowed to use this functionality

        group = CIgroup.objects.get(pk=self.kwargs['pk'])

        if self.request.user.is_staff:
            return True

        # only primary admins can add new admins
        for admin in group.group_primary_admins.all():
            if admin.userprofile == self.request.user.profile:
                return True

        return False

    def get(self, request, *args, **kwargs):
        """this is to select the admin to add"""

        group = CIgroup.objects.get(pk=self.kwargs['pk'])

        if group.location_city:
            local_members_primary = UserProfile.objects.filter(
                location=group.location_city)
        elif group.location_region:
            local_members_primary = UserProfile.objects.filter(
                location__region=group.location_region)
        elif group.location_country:
            local_members_primary = UserProfile.objects.filter(
                location__region__country=group.location_country)
        else:
            render(request, 'error.html')

        # exclude existing primary admins
        # (existing secondary admins are left in b/c you can be promoted)
        # iterates through local members and excludes all admins
        for adminprofile in group.group_primary_admins.all():
            local_members_primary = local_members_primary.exclude(
                id=adminprofile.userprofile.id)

        # we duplicate after the first exclude b/c we don't want
        # any primary admins showing up in selection for secondary ones
        local_members_secondary = local_members_primary

        # exclude existing (primary and secondary) admins for secondary
        # iterates through local members and excludes all admins
        for adminprofile in group.group_secondary_admins.all():
            local_members_secondary = local_members_secondary.exclude(
                id=adminprofile.userprofile.id)

        return render(request, 'CommunityInfrastructure/group_add_admin.html',
                      {'group': group, 'local_members_primary': local_members_primary,
                       'local_members_secondary': local_members_secondary})

    def post(self, request, *args, **kwargs):
        """this is to apply the selection"""

        group = CIgroup.objects.get(pk=self.kwargs['pk'])
        selected_primary_admins_pk = self.request.POST.getlist(
            'select admins primary')
        selected_secondary_admins_pk = self.request.POST.getlist(
            'select admins secondary')

        for admin_pk in selected_primary_admins_pk:
            admin_userprofile = UserProfile.objects.get(id=admin_pk)
            # print(admin_userprofile)
            if hasattr(admin_userprofile, 'linked_admin_profile'):

                admin_userprofile.linked_admin_profile.groups_managed_primary.add(
                    group)
                prim_admin_group = PermGroup.objects.get(
                    name='Primary Group Admin')
                admin_userprofile.user.groups.add(prim_admin_group)

                # if a user was already a secondary admin we remove
                # them from that tier and promote them
                if admin_userprofile.linked_admin_profile.groups_managed_secondary\
                        .filter(id=group.id):
                    admin_userprofile.linked_admin_profile.groups_managed_secondary.remove(
                        group)
                    if not admin_userprofile.linked_admin_profile.groups_managed_secondary.all():
                        sec_admin_group = PermGroup.objects.get(
                            name='Secondary Group Admin')
                        admin_userprofile.user.groups.remove(sec_admin_group)

            # we don't need double submission check here
            # since if it is double submitted the above if will catch it
            else:

                # make a new AdminProfile
                new_profile = AdminProfile(userprofile=admin_userprofile)
                new_profile.save()
                new_profile.groups_managed_primary.add(group)

                prim_admin_group = PermGroup.objects.get(
                    name='Primary Group Admin')

                # either method here works to add the group to the user
                # prim_admin_group.user_set.add(admin_userprofile.user)
                admin_userprofile.user.groups.add(prim_admin_group)

        for admin_pk in selected_secondary_admins_pk:
            admin_userprofile = UserProfile.objects.get(id=admin_pk)
            if hasattr(admin_userprofile, 'linked_admin_profile'):

                admin_userprofile.linked_admin_profile.groups_managed_secondary.add(
                    group)
                sec_admin_group = PermGroup.objects.get(
                    name='Secondary Group Admin')
                admin_userprofile.user.groups.add(sec_admin_group)

            # we don't need double submission check here
            # since if it is double submitted the above if will catch it
            else:

                # make a new AdminProfile
                new_profile = AdminProfile(userprofile=admin_userprofile)
                new_profile.save()
                new_profile.groups_managed_secondary.add(group)

                sec_admin_group = PermGroup.objects.get(
                    name='Secondary Group Admin')

                # either method here works to add the group to the user
                # prim_admin_group.user_set.add(admin_userprofile.user)
                admin_userprofile.user.groups.add(sec_admin_group)

        url = reverse('groups top')
        url += f'/{group.location_country}/{group.slug()}/{group.id}'
        return redirect(url)


class GroupRemoveAdmin(LoginRequiredMixin, UserPassesTestMixin, View):
    """see add admin description"""

    def test_func(self):
        group = CIgroup.objects.get(pk=self.kwargs['pk'])
        if self.request.user.is_staff:
            return True
        # only primary admins can remove admins
        for admin in group.group_primary_admins.all():
            if admin.userprofile == self.request.user.profile:
                return True
        return False

    def get(self, request, *args, **kwargs):
        """this is to select the admin to remove"""
        group = CIgroup.objects.get(pk=self.kwargs['pk'])
        # note: this is selecting AdminProfile instead of user
        # so we need to account for that in the html template
        admins_primary = group.group_primary_admins.all()
        admins_secondary = group.group_secondary_admins.all()
        return render(request, 'CommunityInfrastructure/group_remove_admin.html',
                      {'group': group, 'admins_primary': admins_primary,
                       'admins_secondary': admins_secondary})

    def post(self, request, *args, **kwargs):
        """this is to apply the selection"""

        group = CIgroup.objects.get(pk=self.kwargs['pk'])
        remove_primary_admins_pk = self.request.POST.getlist(
            'remove admins primary')
        remove_secondary_admins_pk = self.request.POST.getlist(
            'remove admins secondary')

        for admin_pk in remove_primary_admins_pk:
            admin_userprofile = UserProfile.objects.get(id=admin_pk)
            if hasattr(admin_userprofile, 'linked_admin_profile'):
                admin_userprofile.linked_admin_profile.groups_managed_primary.remove(
                    group)
                # if a user has no more primary admin roles left we need to remove the role
                if not admin_userprofile.linked_admin_profile.groups_managed_primary.all():
                    prim_admin_group = PermGroup.objects.get(
                        name='Primary Group Admin')
                    admin_userprofile.user.groups.remove(prim_admin_group)
            else:  # an admin profile should always exist to get this far
                render(request, 'error.html')

        for admin_pk in remove_secondary_admins_pk:
            admin_userprofile = UserProfile.objects.get(id=admin_pk)
            if hasattr(admin_userprofile, 'linked_admin_profile'):
                admin_userprofile.linked_admin_profile.groups_managed_secondary.remove(
                    group)
                # if a user has no more secondary admin roles left we need to remove the role
                if not admin_userprofile.linked_admin_profile.groups_managed_secondary.all():
                    sec_admin_group = PermGroup.objects.get(
                        name='Secondary Group Admin')
                    admin_userprofile.user.groups.remove(sec_admin_group)
            else:  # an admin profile should always exist to get this far
                render(request, 'error.html')

        url = reverse('groups top')
        url += f'/{group.location_country}/{group.slug()}/{group.id}'
        return redirect(url)


class ApproveUser(PermissionRequiredMixin, LoginRequiredMixin, View):
    """
    Requires a permission.
    If permission present allows a user
    to grant other users image upload permissions.
    """
    permission_required = ('UserAccounts.approve_users')

    def get(self, request, *args, **kwargs):
        """provide list of valid users to promote"""
        users = get_user_model().objects.all()
        users = users.exclude(groups__permissions__codename="add_userimage")
        user_form = ApproveUserForm()
        return render(request, 'CommunityInfrastructure/approve_user.html',
                      {'unapproved_users_form': user_form})

    def post(self, request, *args, **kwargs):
        """this is to apply the selection"""
        if self.request.POST.get("unapproved_user"):
            user = get_user_model().objects.get(
                id=self.request.POST.get("unapproved_user"))
            perm_group = PermGroup.objects.get(name='Upload Approved')
            user.groups.add(perm_group)
            user.profile.approved_by = self.request.user
            user.profile.save()

            messages.success(request, 'Permission Update Complete')
            url = reverse('approve user')
            return redirect(url)


class GroupCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """groups can currently only be created by staff"""
    model = CIgroup
    form_class = GroupForm

    def form_valid(self, form):
        # add this data first then validate
        form.instance.uploader = self.request.user

        # only one of these fields can be set
        # so if multiple are set we need to reject the submission
        if form.instance.location_city:
            if form.instance.location_region or form.instance.location_country:
                return super().form_invalid(form)
        if form.instance.location_region:
            if form.instance.location_city or form.instance.location_country:
                return super().form_invalid(form)
        if form.instance.location_country:
            if form.instance.location_region or form.instance.location_city:
                return super().form_invalid(form)

        return super().form_valid(form)  # then run original form_valid

    def test_func(self):
        if self.request.user.is_staff:
            return True
        return False


class GroupEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """only primary admins are allowed to edit groups (and only their own)"""
    model = CIgroup
    form_class = GroupForm

    def test_func(self):  # this checks to see if you're allowed to use this functionality
        if self.request.user.is_staff:
            return True
        group = CIgroup.objects.get(pk=self.kwargs['pk'])
        for admin in group.group_primary_admins.all():
            if admin.userprofile == self.request.user.profile:
                return True
        return False

    def form_valid(self, form):
        # add this data first then validate
        form.instance.uploader = self.request.user
        # only one of these fields can be set
        # so if multiple are set we need to reject the submission
        if form.instance.location_city:
            if form.instance.location_region or form.instance.location_country:
                return super().form_invalid(form)
        if form.instance.location_region:
            if form.instance.location_city or form.instance.location_country:
                return super().form_invalid(form)
        if form.instance.location_country:
            if form.instance.location_region or form.instance.location_city:
                return super().form_invalid(form)

        return super().form_valid(form)  # then run original form_valid


class GroupDelete(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
    """only staff can delete groups"""
    model = CIgroup
    success_url = reverse_lazy('groups top')
    context_object_name = 'group'
    permission_required = ('staff')

    def delete(self, request, *args, **kwargs):
        group = self.get_object()
        group_primary_admins = group.group_primary_admins.all()
        group_secondary_admins = group.group_secondary_admins.all()

        # remove permissions for admins before deleting
        for admin in group_primary_admins:
            admin.groups_managed_primary.remove(group)
            # if the list is now empty they also need their permissions removed
            if not admin.groups_managed_primary.all():
                prim_admin_group = PermGroup.objects.get(
                    name='Primary Group Admin')
                admin.userprofile.user.groups.remove(prim_admin_group)
        for admin in group_secondary_admins:
            admin.groups_managed_secondary.remove(group)
            # if the list is now empty they also need their permissions removed
            if not admin.groups_managed_secondary.all():
                sec_admin_group = PermGroup.objects.get(
                    name='Secondary Group Admin')
                admin.userprofile.user.groups.remove(sec_admin_group)

        return super().delete(self, request, *args, **kwargs)


class StudioCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """can only be created by staff. fields support markdown"""
    model = PaintingStudio
    form_class = StudioForm
    permission_required = ('staff')


class StudioEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """only staff and the registered owner can edit. Currently only supports one studio admin."""
    model = PaintingStudio
    form_class = StudioForm

    def test_func(self):
        if self.request.user.is_staff or self.request.user == self.get_object().userprofile:
            return True
        return False


class StudioDetails(FilterView):
    """Displays details on studio, links to website, and a gallery of their official uploads."""
    model = UserImage
    filterset_class = ImageFilter
    context_object_name = 'images'
    paginate_by = 8
    template_name = 'CommunityInfrastructure/paintingstudio_detail.html'

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

            try:
                # show the most recent images first
                queryset = PaintingStudio.objects.get(
                    pk=self.kwargs['pk']).studios_images.all().filter(
                    studioimages__official=True).order_by('-pk')
            except ObjectDoesNotExist as error:
                raise Http404(f'{error}') from error
        else:
            raise ImproperlyConfigured(
                f"{self.__class__.__name__} is missing a QuerySet. Define "
                f"{self.__class__.__name__}.model, {self.__class__.__name__}.queryset, or override "
                f"{self.__class__.__name__}.get_queryset()."
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
        image_filter = ImageFilter(
            self.request.GET, queryset=UserImage.objects.all())
        context['filter_form'] = image_filter
        context['studio'] = PaintingStudio.objects.get(pk=self.kwargs['pk'])
        context['form'] = SelectExport()

        contextregionzone = City.objects.filter(
            region__region_name=PaintingStudio.objects.get(pk=self.kwargs['pk']).location.region)
        if contextregionzone:
            context['zone_container'] = contextregionzone

        if self.request.GET:
            dic_string = dict(self.request.GET)
            if self.request.GET.get('page'):
                dic_string.pop('page')
            context['search'] = dic_string

        return context


class StudioUpload(UserPassesTestMixin, GalleryMultipleUpload):
    """
    GalleryMultipuleUpload will handle setting the image as official
    and sending signals as long as we set
    studio_official_upload to True to enable the functionality

    Only staff and studio admin can upload
    """
    studio_official_upload = True

    def test_func(self):
        return studio_admin_check(self)


class StudioUploadMultipart(UserPassesTestMixin, GalleryUploadMultipart):
    """
    GalleryMultipuleMultipart will handle setting the image as official
    and sending signals as long as we set studio_official_upload
    to True to enable the functionality

    Only staff and studio admin can upload
    """
    studio_official_upload = True

    def test_func(self):
        return studio_admin_check(self)


class StudioExport(LoginRequiredMixin, UserPassesTestMixin, View):
    """when we have selected which platform to use we come here to begin initial configuration"""

    def test_func(self):  # this checks to see if you're allowed to use this functionality
        return studio_admin_check(self)

    def get(self, request, *args, **kwargs):
        """we shouldn't recive get requests to this page"""
        return render(request, 'error.html', {'error': 'other error code'})

    def post(self, request, *args, **kwargs):
        """will return the html page for the appropriate social media platform"""

        # for facebook exports we first need to configure
        #  the account since facebook logins are used as well on the site.
        if self.request.POST.get('platform') == "Facebook":

            studio = PaintingStudio.objects.get(pk=self.kwargs['pk'])
            owner = studio.userprofile

            # a try is used here b/c a token can be null if you submit maliciously
            #  or if you haven't linked a facebook account at all
            try:
                # account is a socialaccount model
                tokenobject = SocialToken.objects.get(
                    account__user=owner)
            except ObjectDoesNotExist:
                messages.error(
                    request, 'you must add a facebook account before you can use this feature')
                return redirect('/accounts/social/connections/')

            userid = SocialAccount.objects.get(user=owner).uid
            # fetch the pages a user is authorized to upload to
            apiurlstring = 'https://graph.facebook.com/v13.0/' + userid \
                + '/accounts?access_token=' + tokenobject.token + ''
            # call the facebook api
            response = requests.get(apiurlstring)
            responsejson = response.json()
            if 'error' in responsejson:
                raise Http404(f'{responsejson}')

            pages_managed = []
            for page in responsejson["data"]:
                var = {'name': page['name'], 'id': page['id']}
                pages_managed = pages_managed + [var]

            count = self.request.POST.get('select_number')
            return render(request, 'CommunityInfrastructure/export_select_facebook.html',
                          {'pages_managed': pages_managed, 'count': count, 'studio': studio})

        # for instagram exports we first need to configure the account
        # since it uses facebook api and facebook logins are used as well on the site.
        if self.request.POST.get(
                'platform') == "Instagram":
            studio = PaintingStudio.objects.get(pk=self.kwargs['pk'])
            owner = studio.userprofile
            # tokens and user id's should already exist because
            #  of facebook login/permission escalation being step one

            # a try is used here b/c a token can be null if you submit maliciously
            # or if you haven't linked a facebook account at all
            try:
                tokenobject = SocialToken.objects.get(
                    account__user=owner)  # account is a socialaccount model
            except ObjectDoesNotExist:
                messages.error(
                    request, 'you must add a facebook account before you can use this feature')
                return redirect('/accounts/social/connections/')

            userid = SocialAccount.objects.get(user=owner).uid
            # fetch the pages a user is authorized to upload to
            apiurlstring = 'https://graph.facebook.com/v13.0/' \
                + userid + '/accounts?access_token=' + tokenobject.token + ''
            response = requests.get(apiurlstring)  # call the facebook api
            responsejson = response.json()

            if 'error' in responsejson:
                raise Http404(f'{responsejson}')

            pages_managed = []
            for page in responsejson["data"]:
                var = {'name': page['name'], 'id': page['id']}
                pages_managed = pages_managed + [var]

            count = self.request.POST.get('select_number')
            return render(request, 'CommunityInfrastructure/export_select_instagram.html',
                          {'pages_managed': pages_managed, 'count': count, 'studio': studio})

        return render(request, 'error.html', {'error': 'error code'})


class StudioRequestFacebook(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    continue the process of a facebook image upload by selecting the album
    or if that has already been done upload the images
    """

    def test_func(self):
        if self.request.user.is_staff or self.request.user == PaintingStudio.objects.get(
                pk=self.kwargs['pk']).userprofile:
            return True
        return False

    def post(self, request, *args, **kwargs):
        """
        returns the page to select album
        or if an album is provided returns studio details on success
        """

        studio = PaintingStudio.objects.get(pk=self.kwargs['pk'])
        owner = studio.userprofile
        tokenobject = SocialToken.objects.get(
            account__user=owner)  # account is a socialaccount model

        if self.request.POST.get('select_album'):
            # if albumid is maliciously set it will just cause the facebook api call to fail.
            # Entering this check early by artificially adding the parameter
            # looks like it will be handled by the api fail error state
            albumid = self.request.POST.get('select_album')
            count_input = self.request.POST.get('count')
            try:
                count = int(count_input)
            except TypeError as error:
                raise Http404(
                    f'error: {count_input} has not been called correctly you hacker. \
                        Error: {error}') from error
            # we replicate the way images are displayed on the studio page
            # for consistant uploading selection
            studios_images = PaintingStudio.objects.get(pk=studio.pk).studios_images.all().filter(
                studio_images__official=True).order_by('-pk')

            # now that we have all the information
            # we need to call the api to get the page access token
            userid = SocialAccount.objects.get(user=owner).uid
            apiurlstringforpage = 'https://graph.facebook.com/v13.0/' + \
                userid + '/accounts?access_token=' + tokenobject.token
            pages = requests.get(apiurlstringforpage).json()
            if 'error' in pages:
                messages.error(request,
                               'The request returned an error. \
                                Make sure you have enabled the appropriate permissions')
                redirect(request.META['HTTP_REFERER'])
            # there might be multipule pages available
            pagetoken = ''
            for page in pages['data']:
                if page['id'] == self.request.POST.get('page_id'):
                    pagetoken = page['access_token']

            if not pagetoken:
                raise Http404('error: unable to resolve page access')

            if count > 10 or count < 1:
                raise Http404(
                    f'error: {count} has not been called correctly you hacker')

            # now that we have the page token we can upload the images
            for i in range(count):
                description = studios_images[i].image_title
                imageurl = studios_images[i].image.url
                apiurlstring = 'https://graph.facebook.com/v13.0/' \
                    + albumid + '/photos?caption=' + \
                    description + '&url=' + imageurl + '&access_token=' + pagetoken
                responsejson = requests.post(apiurlstring).json()
                if 'error' in responsejson:
                    return render(request, 'error.html', {'error': f'{responsejson}'})
            test = responsejson
            messages.success(request, 'Image Export Complete!')
            url = reverse('groups top')
            url += f'/paintingstudio/{studio.slug()}/{studio.id}'
            return redirect(url)

        # here we take the page id and find available albums to post in.
        # an improperly named select_page will simply cause the api lookup to fail
        if self.request.POST.get(
                'select_page'):

            pageid = self.request.POST.get('select_page')
            apiurlstring = 'https://graph.facebook.com/v13.0/' + \
                pageid + '/albums?access_token=' + tokenobject.token
            responsejson = requests.get(apiurlstring).json()
            if 'error' in responsejson:
                messages.error(request,
                               'The request returned an error. \
                                Make sure you have enabled the appropriate permissions')
                redirect(request.META['HTTP_REFERER'])

            # get a list of albums
            albums = []
            for album in responsejson["data"]:
                var = {'name': album['name'], 'id': album['id']}
                albums = albums + [var]
            test = 'placeholder'
            test2 = tokenobject
            # still need this in the future will confirm it hasn't been tampered with later
            count = self.request.POST.get('count')

            return render(request, 'CommunityInfrastructure/exportfacebook.html',
                          {'test': test, 'test2': test2, 'albums': albums,
                           'page_id': pageid, 'count': count, 'studio': studio})

        raise Http404('post error')


class StudioRequestInstagram(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    continue the process of a facebook image upload by selecting the album
    or if that has already been done upload the images
    """

    def test_func(self):
        return studio_admin_check(self)

    def post(self, request, *args, **kwargs):
        """Applies the Export. Redirects to studio page when complete"""

        studio = PaintingStudio.objects.get(pk=self.kwargs['pk'])
        owner = studio.userprofile
        tokenobject = SocialToken.objects.get(
            account__user=owner)  # account is a socialaccount model

        # here we take the page id and find available albums to post in.
        # an improperly named select_page will simply cause the api lookup to fail
        if self.request.POST.get('select_page'):
            pageid = self.request.POST.get('select_page')
            caption = self.request.POST.get('caption')
            carousel_id = None
            count_input = self.request.POST.get('count')
            try:
                count = int(count_input)
            except TypeError as error:
                raise Http404(
                    f'error: {count_input} has not been called correctly you hacker') from error
            apiurlstring = 'https://graph.facebook.com/v13.0/' + pageid + \
                '?fields=instagram_business_account&access_token=' + tokenobject.token
            if count > 10 or count < 1:
                raise Http404('not this time')

            # call the API to get the instagram_business_account
            responsejson = requests.get(apiurlstring).json()
            if 'error' in responsejson:
                messages.error(request,
                               'The request returned an error. \
                                Make sure you have enabled the appropriate permissions')
                redirect(request.META['HTTP_REFERER'])

            if not 'instagram_business_account' in responsejson:
                raise Http404(
                    f'Misconfigured Response \
                        (this can happen if your permissions are not set up properly):\
                             {responsejson}')
            igid = responsejson["instagram_business_account"]['id']

            if count == 1:
                studio_image_set = PaintingStudio.objects.get(
                    pk=studio.pk).studios_images.all().filter(
                    studio_images__official=True).order_by('-pk')
                image_url = studio_image_set[0].image.url
                apiurlstring2 = 'https://graph.facebook.com/v13.0/' + igid + \
                    '/media?image_url=' + image_url + '&access_token=' + tokenobject.token
                if not caption == '':
                    apiurlstring2 += ('&caption=' +
                                      urllib.parse.quote(caption))
                # call the API
                responsejson2 = requests.post(apiurlstring2).json()
                if 'error' in responsejson2:
                    raise Http404(
                        f'initial upload error: \n{apiurlstring2}\n{responsejson2}')
                if not 'id' in responsejson2:
                    raise Http404(f'Misconfigured Response: {responsejson2}')
                image_post_id = responsejson2['id']
                apiurlstring3 = 'https://graph.facebook.com/v13.0/' + igid + \
                    '/media_publish?creation_id=' + image_post_id + \
                    '&access_token=' + tokenobject.token
                # call the API
                responsejson3 = requests.post(apiurlstring3).json()
                if 'error' in responsejson3:
                    raise Http404(f'publish error: {responsejson3}')

            else:
                image_post_id_list = []
                for i in range(count):

                    # ordered with most recent first
                    studio_image_set = PaintingStudio.objects.get(
                        pk=studio.pk).studios_images.all().filter(
                        studio_images__official=True).order_by('-pk')
                    image_url = studio_image_set[i].image.url
                    apiurlstring2 = 'https://graph.facebook.com/v13.0/' \
                                    + igid + '/media?image_url=' + image_url \
                                    + '&is_carousel_item=true&access_token=' + tokenobject.token
                    # call the API
                    responsejson2 = requests.post(apiurlstring2).json()
                    if 'error' in responsejson2:
                        raise Http404(
                            f'misconfigured image upload request:\
                                \n{apiurlstring2}\n{responsejson2}')
                    if not 'id' in responsejson2:
                        raise Http404(
                            f'Misconfigured Response: {responsejson2}')
                    image_post_id_list += [responsejson2['id']]

                apiurlstring3 = 'https://graph.facebook.com/v13.0/' + igid + \
                    '/media?media_type=CAROUSEL&access_token=' + tokenobject.token + '&children='
                first = True
                children = ''
                for i in image_post_id_list:
                    if first:
                        children += i
                        first = False
                    else:
                        children += ',' + i

                # documentation leaves this part out
                # but the list is supposed to be url encoded commas
                children = urllib.parse.quote(
                    children)
                apiurlstring3 += children
                if not caption == '':
                    # this will encode everything not just
                    #  the # that the docs specifically call for
                    apiurlstring3 += ('&caption=' + urllib.parse.quote(
                        caption))
                # call the API
                responsejson3 = requests.post(apiurlstring3).json()
                if 'error' in responsejson3:
                    raise Http404(
                        f'misconfigured carousel creation request:\
                            \n{apiurlstring3}\n{responsejson3}')
                if not 'id' in responsejson3:
                    raise Http404(f'Misconfigured Response: {responsejson3}')
                carousel_id = responsejson3['id']

                apiurlstring4 = 'https://graph.facebook.com/v13.0/' + igid + \
                    '/media_publish?creation_id=' + carousel_id + \
                    '&access_token=' + tokenobject.token
                # call the API
                responsejson4 = requests.post(apiurlstring4).json()
                if 'error' in responsejson4:
                    raise Http404(f'publish error: {responsejson4}')

            # this gets a list of our instagram posts
            apiurlstring2 = 'https://graph.facebook.com/v13.0/' + \
                igid + '/media?access_token=' + tokenobject.token
            responsejson2 = requests.get(apiurlstring2).json()

            messages.success(request, 'Image Export Complete!')
            url = reverse('groups top')
            url += f'/paintingstudio/{studio.slug()}/{studio.id}'
            return redirect(url)

        raise Http404('post error')


class CountryCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """adds a new country to the DB can be done with anyone with the add_country permission"""
    model = Country
    form_class = CountryForm
    template_name = 'GameData/game_data_form.html'
    permission_required = ('GameData.add_country')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        # context['news'] = calculate_news_bar()
        image_filter = ImageFilter(
            self.request.GET, queryset=UserImage.objects.all())
        context['filter_form'] = image_filter
        return context

class RegionCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """adds a new region to the DB can be done with anyone with the add_region permission"""
    model = Region
    form_class = RegionForm
    template_name = 'GameData/game_data_form.html'
    permission_required = ('GameData.add_region')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        # context['news'] = calculate_news_bar()
        image_filter = ImageFilter(
            self.request.GET, queryset=UserImage.objects.all())
        context['filter_form'] = image_filter
        return context


class CityCreate(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    """adds a new city to the DB can be done with anyone with the add_city permission"""
    model = City
    form_class = CityForm
    template_name = 'GameData/game_data_form.html'
    permission_required = ('GameData.add_city')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        # context['news'] = calculate_news_bar()
        image_filter = ImageFilter(
            self.request.GET, queryset=UserImage.objects.all())
        context['filter_form'] = image_filter
        return context
