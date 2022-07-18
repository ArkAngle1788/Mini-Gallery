from django.shortcuts import render


# from django.http import HttpResponseRedirect
# from GameData.models import Games, Faction, Faction_Type, Sub_Faction
from .models import Match, Player, League,Season, Player_season_faction, Round
# from UserAccounts.models import UserProfile
# from .custom_functions import *
# from django.db.models import Q
# from django.http import HttpResponseNotFound
# from django.views import View
# from django.views.generic import UpdateView
# from django.views.generic.edit import CreateView, DeleteView
# from UserAccounts.models import UserProfile
# from Gallery.models import Professional
# from ContentPost.models import ContentPost
# from django.urls import reverse
# from django.contrib.auth.decorators import login_required
# from django.contrib.auth.mixins import LoginRequiredMixin,UserPassesTestMixin
# from .forms import *
# from django.contrib import messages
# from django.urls import reverse_lazy



# actual league views backed up elsewhere since I probably will want to completly rewrite most of them.


def leagues(request):

    return render(request,'CommunityInfrastructure/home.html')
