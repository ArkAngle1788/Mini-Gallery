from django.apps import AppConfig


class GalleryConfig(AppConfig):
    name = 'Gallery'

    def ready(self):
        import Gallery.signals
