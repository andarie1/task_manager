import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Task
import random

EMOJI_REACTIONS = ["✅", "✨", "⚡"]

@receiver(post_save, sender=Task)
def task_status_changed(sender, instance, **kwargs):
    if instance.last_status != instance.status and instance.last_status is not None:
        emoji = random.choice(EMOJI_REACTIONS)
        print(f"{emoji} Задача обновлена: {instance.title}, новый статус: {instance.status} (был: {instance.last_status})")

        # Отправка email-уведомления
        subject = f'Статус задачи "{instance.title}" изменен'
        message = f'Статус задачи "{instance.title}" был изменен с "{instance.last_status}" на "{instance.status}".'
        from_email = os.getenv('EMAIL_HOST_USER')
        if from_email is None:
            print("Ошибка: EMAIL_HOST_USER не найден в .env")
            return
        recipient_list = [instance.owner.email]

        send_mail(subject, message, from_email, recipient_list)
    else:
        print(" (post_save) Статус не изменился, уведомление не отправляем")











