# neumatico/apps.py
from django.apps import AppConfig

class NeumaticoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'neumatico'

    def ready(self):
        import neumatico.signals  # Importa las señales
