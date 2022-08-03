from django.shortcuts import redirect
from UserAccounts.models import UserProfile
from django.views import View
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from ContentPost.custom_functions import calculate_news_bar
from .forms import *
from Gallery.filters import ImageFilter
from Gallery.models import UserImage
from django_filters.views import FilterView

from django.urls import reverse

class Self_Profile(LoginRequiredMixin,View):

    def get(self, request,*args,**kwargs):
        url=reverse('profile', args=[self.request.user.profile.pk])
        return redirect(url)

# note that this currently transmits all user data so if the model contains private information we will need to clense that
class Profile(FilterView):
    model=UserImage
    filterset_class=ImageFilter
    context_object_name='images'
    paginate_by=8
    template_name='UserAccounts/userprofile_detail.html'

    def get_queryset(self):

        queryset=UserImage.objects.filter(uploader__profile__pk=self.kwargs['pk'])

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
        image_filter=ImageFilter(self.request.GET, queryset=UserImage.objects.all())
        context['filter_form']=image_filter
        context['profile']=UserProfile.objects.get(pk=self.kwargs['pk'])
        context['news']=calculate_news_bar()

        if self.request.GET:
            dic_string=dict(self.request.GET)
            if self.request.GET.get('page'):
                dic_string.pop('page')
            context['search']=dic_string

        return context

class ProfileUpdate(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=UserProfile
    form_class=ProfileEditForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['news']=calculate_news_bar()
        return context

    def test_func(self):
        if self.request.user.is_staff or self.get_object().pk==self.request.user.profile.pk:
            return True
        return False
