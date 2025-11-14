from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    
    def ready(self):
        """Ejecutar código cuando la aplicación esté lista"""
        try:
            # Importar nuestras configuraciones personalizadas del admin
            from . import admin_init
        except ImportError:
            pass
