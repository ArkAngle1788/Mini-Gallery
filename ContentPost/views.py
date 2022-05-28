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

# leagues_nav=League.objects.filter(child_season__current_season__isnull=False)
leagues_nav='hi'





class ContentPostListView(ListView):
    model=ContentPost
    context_object_name='content_posts'
    ordering=['-headline','-date_posted']
    paginate_by=5



    def get_queryset(self):
        if self.request.GET.get('search'):

            search_title=ContentPost.objects.filter(title__icontains=self.request.GET.get('search'))
            search_author=ContentPost.objects.filter(author__profile__league_profile__player_name__icontains=self.request.GET.get('search'))

            posts=search_title | search_author
            posts=posts.order_by('-date_posted')

            # var=Paginator(posts,2)
            # context['page_obj']=var

            # context['content_posts']=posts
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
        
        # print(self.get_permission_required())

        # print('detail view')
        # print(default_storage.__class__)
        # print(default_storage.exists('ContentPost_images/sad_zealot.png'))
        # print(context['object'].image1.name)
        # # default_storage.delete('ContentPost_images/sad_zealot.png')
        # print(default_storage.exists('ContentPost_images/sad_zealot.png'))

        return context





class ContentPostCreateView(PermissionRequiredMixin,UserPassesTestMixin,CreateView):  #shares a template with update view -- <model>_form.html
    model=ContentPost
    form_class=ContentPostForm
    permission_required = ('ContentPost.add_contentpost')

#over ride the form_valid method to add information to the form before it is submitted

    def form_valid(self,form):
        form.instance.author=self.request.user #add this data first then validate
        # form.instance.title="None"
        # form.save()
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


        # form.fields['mother'].queryset = Person.objects.filter(family)
        # form.fields['father'].queryset = Person.objects.filter(family)



    def test_func(self):
        #can only create if you're a Content creator user or better
        # if self.request.user.profile.permission_level<=15:
        #     return True
        return True

# this view uses passes test instead of permissionmixin because you might lose edit privilages but you should still be able to edit somethign you wrote
class ContentPostUpdateView(LoginRequiredMixin,UserPassesTestMixin,UpdateView):  #shares a template with update view -- <model>_form.html
    model=ContentPost
    # fields=['headline','title','text1','image1','text2','image2','text3','image3','global_display','display_to_game','source']
    form_class=ContentPostForm


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in the leaguenav QuerySet
        context['league_nav'] = leagues_nav
        context['news']=calculate_news_bar()
        return context

    def test_func(self):

        #this makes it so you can only edit you own post unless you're a higher level admin
        blog_post=self.get_object()


        #can only edit if you're the post author or if you have edit permissions (given by some groups)
        if self.request.user==blog_post.author or self.request.user.has_perm("ContentPost.change_contentpost"):

# user.has_perm('foo.change_bar')
# permission_required = ('ContentPost.create_contentpost')
# if request.user.groups.filter(name="group_name").exists():

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

    def delete(self, request, *args, **kwargs):

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
