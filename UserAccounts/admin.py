from django.contrib import admin

from .models import AdminProfile, UserProfile

admin.site.register(UserProfile)
admin.site.register(AdminProfile)
