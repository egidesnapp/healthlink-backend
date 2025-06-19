# healthlink-backend/api/apps.py

from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'HealthLink API' # Optional: A more descriptive name for the admin site

    def ready(self):
        # Import your signals here so they are registered when the app is ready
        import api.signals