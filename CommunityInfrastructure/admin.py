from django.contrib import admin

from .models import City, Country, Group, Language, PaintingStudio, Region

admin.site.register(Group)
admin.site.register(PaintingStudio)
admin.site.register(Language)
admin.site.register(Country)
admin.site.register(Region)
admin.site.register(City)
