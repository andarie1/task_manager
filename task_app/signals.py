from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Task
import random


EMOJI_REACTIONS = [ "✅","✨", "⚡"]


@receiver(post_save, sender=Task)
def task_status_changed(sender, instance, **kwargs):
    if instance.last_status != instance.status and instance.last_status is not None:
        emoji = random.choice(EMOJI_REACTIONS)
        print(f"{emoji} Задача обновлена: {instance.title}, новый статус: {instance.status} (был: {instance.last_status})")
    else:
        print(" (post_save) Статус не изменился, уведомление не отправляем")









