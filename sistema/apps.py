from django.apps import AppConfig


class SistemaConfig(AppConfig):
    name = "sistema"
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        import sistema.signals  # noqa: F401
