from django.apps import AppConfig


class UseraccountsConfig(AppConfig):
    name = 'UserAccounts'
    def ready(self):
        import UserAccounts.signals
