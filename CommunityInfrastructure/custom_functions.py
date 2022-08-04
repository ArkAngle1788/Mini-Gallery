import django.dispatch
from .models import PaintingStudio

# this is for creating the through link model
new_studio_image = django.dispatch.Signal()

def studio_official_send(self,image):

    studio=PaintingStudio.objects.get(pk=self.kwargs['pk'])

    try:
        image.paintingstudio.get(id=studio.id)
    except:
        image.paintingstudio.add(studio)

    new_studio_image.send(sender=self.__class__, image=image, studio=studio)
