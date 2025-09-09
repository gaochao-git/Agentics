from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agents.core'
    
    def ready(self):
        # Django启动时不立即初始化智能体，避免在makemigrations时出错
        pass