from django.contrib import admin
from .models import League,Season,Player,Player_season_faction,Round,Match

admin.site.register(League)
admin.site.register(Season)
admin.site.register(Player)
admin.site.register(Player_season_faction)
admin.site.register(Round)
admin.site.register(Match)
