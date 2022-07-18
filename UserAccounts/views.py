from django.shortcuts import render
from UserAccounts.models import UserProfile
from django.views import View
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from ContentPost.custom_functions import calculate_news_bar
from .forms import *

class Self_Profile(LoginRequiredMixin,View):

    def get(self, request,*args,**kwargs):
        return render(request, 'UserAccounts/userprofile_self.html',{'news':calculate_news_bar()})


# note that this currently transmits all user data so if the model contains private information we will need to clense that
class Profile(DetailView):
    model=UserProfile
    context_object_name='profile'

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
