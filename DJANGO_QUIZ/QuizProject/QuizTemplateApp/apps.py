from django.apps import AppConfig


class QuiztemplateappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'QuizTemplateApp'
    
    def ready(self):
        import QuizTemplateApp.signals