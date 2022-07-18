from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from CommunityInfrastructure.models import Group
from GameData.models import Games

# this is easy to expand to be more dynamic but right not it doesn't need to be


class ContentPost(models.Model):


    title=models.CharField(max_length=50)

    text1=models.CharField(max_length=2500,blank=True,null=True)
    image1 = models.ImageField(upload_to='ContentPost_images',blank=True,null=True)
    text2=models.CharField(max_length=2500,blank=True,null=True)
    image2 = models.ImageField(upload_to='ContentPost_images',blank=True,null=True)
    text3=models.CharField(max_length=2500,blank=True,null=True)
    image3 = models.ImageField(upload_to='ContentPost_images',blank=True,null=True)

    headline=models.BooleanField(default=False)
    date_posted=models.DateTimeField(default=timezone.now)
    author=models.ForeignKey(User,on_delete=models.CASCADE)


    # this determines if a post is broadcast globally (wtihin a game type)
    global_display=models.BooleanField(default=False)
    # determine the game type to display message to
    display_to_game=models.ManyToManyField(Games,related_name='relevant_content_posts')


    # linking to a league is how we will currently determine what pages to display praticular items on
    source=models.ForeignKey(Group,on_delete=models.CASCADE,blank=True,null=True)


    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog detail',kwargs={'pk':self.pk})
