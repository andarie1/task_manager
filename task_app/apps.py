from django.apps import AppConfig
import importlib

class TaskAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_app'

    def ready(self):
        importlib.import_module('task_app.signals')


