from django.shortcuts import render
from UserAccounts.models import UserProfile
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.views import View
from ContentPost.custom_functions import calculate_news_bar
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
