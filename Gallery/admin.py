from django.contrib import admin
from .models import UserImage,UserSubImage,Conversion,Scale_Of_Image,Colour,Colour_Catagory,Colour_Priority,TempImage

admin.site.register(UserImage)
admin.site.register(UserSubImage)
admin.site.register(TempImage)
admin.site.register(Conversion)
admin.site.register(Scale_Of_Image)
admin.site.register(Colour)
admin.site.register(Colour_Priority)
admin.site.register(Colour_Catagory)
