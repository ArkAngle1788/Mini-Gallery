from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import ContentPost
from django.urls import reverse_lazy
from django.core.paginator import Paginator


from .custom_functions import *
from .forms import *

from GameData.models import Games

# for sidebar
from League.models import League

# this is here under the presumption that we will want to display league info on the sidebars of the post pages. This might change as implemntation/scope gets updated.
leagues_nav='placeholder'



class ContentPostListView(ListView):
    model=ContentPost
    context_object_name='content_posts'
    ordering=['-headline','-date_posted']
    paginate_by=10


    def get_queryset(self):
        if self.request.GET.get('search'):

            search_title=ContentPost.objects.filter(title__icontains=self.request.GET.get('search'))
            search_author=ContentPost.objects.filter(author__profile__league_profile__player_name__icontains=self.request.GET.get('search'))

            posts=search_title | search_author
            posts=posts.order_by('-date_posted')

            return posts

        return super().get_queryset()


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        context['league_nav'] = leagues_nav

        if self.request.GET.get('search'):
            context['search']=self.request.GET.get('search')

        return context


class ContentPostDetailView(DetailView):
    model=ContentPost

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()

        return context


class ContentPostCreateView(PermissionRequiredMixin,CreateView):
    model=ContentPost
    form_class=ContentPostForm
    permission_required = ('ContentPost.add_contentpost')

    #override the form_valid method to add information to the form before it is submitted
    def form_valid(self,form):
        #if content posts get plugged into the league system then we need a check here to make sure your post is properly linked to groups your allowed to make posts for
        form.instance.author=self.request.user #add this data first then validate
        if ContentPost.objects.filter(title=form.instance.title):
            form.errors['title']=["a post with this title already exists"]
            return super().form_invalid(form)
        return super().form_valid(form) # then run original form_valid


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        # the following syntax will allow us to display only valid choices for the user
        # for proper security form validate will also need to check since this doesn't stop a user from maliciously changing things
        context['form'].fields['display_to_game'].queryset=Games.objects.filter(pk=1)
        return context



# this view uses passes test instead of permissionmixin because you might lose edit privilages but you should still be able to edit somethign you wrote
class ContentPostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):
    model=ContentPost
    form_class=ContentPostForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        return context

    def test_func(self):#this makes it so you can only edit you own post unless you're a higher level admin
        #if content posts get plugged into the league system then we need a check here to make sure your post is properly linked to groups your allowed to edit posts for

        blog_post=self.get_object()
        #can only edit if you're the post author or if you have edit permissions (given by some groups)
        if self.request.user==blog_post.author or self.request.user.has_perm("ContentPost.change_contentpost"):
            return True
        return False


class ContentPostDeleteView(PermissionRequiredMixin,DeleteView):
    model=ContentPost
    success_url=reverse_lazy('blog list')  # Note from docs:    We have to use reverse_lazy() instead of reverse(), as the urls are not loaded when the file is imported.
    permission_required = ('ContentPost.delete_contentpost')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        return context

    def delete(self, request, *args, **kwargs):#override delete to remove images from storage when deleted
        object=self.get_object()

        if object.image1:
            image1_name=object.image1.name
            default_storage.delete(image1_name)
        if object.image2:
            image2_name=object.image2.name
            default_storage.delete(image2_name)
        if object.image3:
            image3_name=object.image3.name
            default_storage.delete(image3_name)

        return super().delete(self,request,*args,**kwargs)
