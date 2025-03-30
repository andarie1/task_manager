from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task

@receiver(post_save, sender=Task)
def task_status_changed(sender, instance, created, **kwargs):
    """
    Сигнал отправляет уведомление пользователю, если статус задачи изменился.
    """
    if not created:  # Проверяем, что PUT
        print(f"✅ Задача обновлена: {instance.title}, новый статус: {instance.status}")



