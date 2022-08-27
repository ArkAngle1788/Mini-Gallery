from django.http import Http404
import django.dispatch
from django.core.exceptions import ObjectDoesNotExist

from .models import PaintingStudio

# this is for creating the through link model
new_studio_image = django.dispatch.Signal()


def studio_official_send(self, image):
    """sends the signal to update_studio_images"""

    try:
        studio = PaintingStudio.objects.get(pk=self.kwargs['pk'])
    except ObjectDoesNotExist as error:
        raise Http404(f'{error}') from error

    # if the studio the image is being posted from is
    # not listed we add it first
    if not image.paintingstudio.filter(id=studio.id):
        image.paintingstudio.add(studio)

    new_studio_image.send(sender=self.__class__, image=image, studio=studio)


def studio_admin_check(self):
    """
    permission check for admin level control over painting studio pages.
    Returns True if user has valid permissions and false otherwise
    """
    # the studio you're uploading to is always part of the url
    if self.request.user.is_staff or self.request.user == PaintingStudio.objects.get(
            pk=self.kwargs['pk']).userprofile:
        return True
    return False
