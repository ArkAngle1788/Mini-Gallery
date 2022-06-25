from django.shortcuts import render
from UserAccounts.models import UserProfile
from django.views import View
from django.views.generic import DetailView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from ContentPost.custom_functions import calculate_news_bar
from .forms import *
# from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

class Self_Profile(LoginRequiredMixin,View): #what are the security implications of building everything from requst.user?


    def get(self, request,*args,**kwargs):

        return render(request, 'UserAccounts/userprofile_self.html',{'news':calculate_news_bar()})



# note that this currently transmits all user data so if the model contains private information we will need to clense that
class Profile(DetailView):
    model=UserProfile
    context_object_name='profile'


# group=Group.objects.get(name="name_of_group")
# request.user.groups.add(group)


# if request.user.groups.filter(name="group_name").exists():


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
