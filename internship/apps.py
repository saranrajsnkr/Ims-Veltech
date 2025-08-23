from django.apps import AppConfig

class InternshipConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'internship'

    def ready(self):
        import internship.signals
        
        
class PortalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portal'

    def ready(self):
        import portal.signals
