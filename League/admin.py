from django.contrib import admin

from .models import League, Match, PlayerSeasonFaction, Round, Season

admin.site.register(League)
admin.site.register(Season)
admin.site.register(PlayerSeasonFaction)
admin.site.register(Round)
admin.site.register(Match)
