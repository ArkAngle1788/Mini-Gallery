from django.contrib import admin
from .models import PaintingStudio,Language,Country,Region,City,Group

admin.site.register(Group)
admin.site.register(PaintingStudio)
admin.site.register(Language)
admin.site.register(Country)
admin.site.register(Region)
admin.site.register(City)
