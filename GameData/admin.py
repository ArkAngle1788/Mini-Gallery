from django.contrib import admin
from .models import Games,Faction_Type,Faction,Sub_Faction,Unit_Type

admin.site.register(Games)
admin.site.register(Faction_Type)
admin.site.register(Faction)
admin.site.register(Sub_Faction)
admin.site.register(Unit_Type)
