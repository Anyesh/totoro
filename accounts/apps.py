from django.apps import AppConfig


class AccountConfig(AppConfig):
    name = "accounts"

    def ready(self):
        # signals are imported, so that they are defined and can be used
        import accounts.signals  # noqa
