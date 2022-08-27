from django.contrib import admin

from .models import Faction, FactionType, Game, SubFaction, UnitType

admin.site.register(Game)
admin.site.register(FactionType)
admin.site.register(Faction)
admin.site.register(SubFaction)
admin.site.register(UnitType)
