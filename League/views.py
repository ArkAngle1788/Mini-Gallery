# from UserAccounts.models import UserProfile
# from Gallery.models import Professional
# from ContentPost.models import ContentPost
from django.urls import reverse
# from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.shortcuts import render
# from django.contrib import messages
# from django.urls import reverse_lazy
# from .custom_functions import *
# from django.db.models import Q
# from django.http import HttpResponseNotFound
# from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from Gallery.models import UserImage
from UserAccounts.models import UserProfile

from .forms import LeagueForm
# from django.http import HttpResponseRedirect
# from GameData.models import Games, Faction, Faction_Type, Sub_Faction
from .models import League#,Season, PlayerSeasonFaction, Round,Match
from CommunityInfrastructure.models import Group

# actual league views backed up elsewhere since I probably will want to
# completly rewrite most of them.



def leagues(request):
    """docstring"""

    image = UserProfile.objects.all()

    var = image.filter(id=200)
    print(var)

    var2 = UserImage.objects.all()[0]
    var2.paintingstudio.get(id=1)
    print(var2)
    print(var2.paintingstudio.get(id=1))

    print("fstring test")
    print(f"{var2}.model, {var2}.queryset, or override {var2}.get_queryset().")

    try:
        image.get(id=23)
    except ImproperlyConfigured:
        print('hi')
    except ObjectDoesNotExist as error:
        print('in except')
        print(error)
        # raise error
    else:
        print('try statement else')

    return render(request, 'CommunityInfrastructure/home.html')

class LeagueCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    """can only be created by staff. fields support markdown"""
    model = League
    form_class = LeagueForm
    permission_required = ('staff')

    def test_func(self):
        if self.request.user.is_staff or self.request.user == self.get_object().userprofile:
            return True
        return False

    def form_valid(self, form):
        #group_id cannot be null so we must add it to the form info
        owning_group=Group.objects.get(pk=self.kwargs['pk'])
        form.instance.group=owning_group
        valid_object=super().form_valid(form)  # then run original form_valid
        return valid_object


class LeagueEdit(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """only staff and the registered owner can edit. Currently only supports one studio admin."""
    model = League
    form_class = LeagueForm

    def test_func(self):
        if self.request.user.is_staff or self.request.user == self.get_object().userprofile:
            return True
        return False


class LeagueDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """only staff can delete groups"""
    model = League
    # success_url = reverse_lazy('groups top')
    

    # context_object_name = 'group'
    # permission_required = ('staff')

    # probably need custom delete logic
    # def delete(self, request, *args, **kwargs):
    #     group = self.get_object()
    #     group_primary_admins = group.group_primary_admins.all()
    #     group_secondary_admins = group.group_secondary_admins.all()

    #     # remove permissions for admins before deleting
    #     for admin in group_primary_admins:
    #         admin.groups_managed_primary.remove(group)
    #         # if the list is now empty they also need their permissions removed
    #         if not admin.groups_managed_primary.all():
    #             prim_admin_group = PermGroup.objects.get(
    #                 name='Primary Group Admin')
    #             admin.userprofile.user.groups.remove(prim_admin_group)
    #     for admin in group_secondary_admins:
    #         admin.groups_managed_secondary.remove(group)
    #         # if the list is now empty they also need their permissions removed
    #         if not admin.groups_managed_secondary.all():
    #             sec_admin_group = PermGroup.objects.get(
    #                 name='Secondary Group Admin')
    #             admin.userprofile.user.groups.remove(sec_admin_group)

    #     return super().delete(self, request, *args, **kwargs)
    def test_func(self):
        if self.request.user.is_staff or self.request.user == self.get_object().userprofile:
            return True
        return False

    def get_success_url(self):
        url=reverse('group info',args=['region',self.object.group.slug(),self.object.group.id])
       
        return url

class LeagueView(DetailView):
    """Viewing leagues is public"""
    model = League

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet and searchbar sets
        # context['league_nav'] = leagues_nav
        context['group'] = self.object.group
        return context
