from django.apps import AppConfig


class CommunityinfrastructureConfig(AppConfig):
    name = 'CommunityInfrastructure'
    def ready(self):
        import CommunityInfrastructure.signals
