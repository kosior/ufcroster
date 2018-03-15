from django.apps import AppConfig


class FightersConfig(AppConfig):
    name = 'fighters'

    def ready(self):
        import fighters.signals
