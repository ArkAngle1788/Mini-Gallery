from django.contrib import admin

from .models import (Colour, ColourCatagory, ColourPriority, Conversion,
                     ScaleOfImage, TempImage, UserImage, UserSubImage)

admin.site.register(UserImage)
admin.site.register(UserSubImage)
admin.site.register(TempImage)
admin.site.register(Conversion)
admin.site.register(ScaleOfImage)
admin.site.register(Colour)
admin.site.register(ColourPriority)
admin.site.register(ColourCatagory)
