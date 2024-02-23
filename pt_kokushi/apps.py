from django.apps import AppConfig

class PtKokushiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'pt_kokushi'
    
    def ready(self):
        import pt_kokushi.signals
