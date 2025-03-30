from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)

    def soft_delete(self):
        """Мягкое удаление категории"""
        self.is_deleted = True
        self.save(update_fields=['is_deleted'])

    def restore(self):
        """Восстановление категории"""
        self.is_deleted = False
        self.save(update_fields=['is_deleted'])

    def __str__(self):
        return self.name


class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name='tasks', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    last_status = models.CharField(max_length=20, choices=STATUS_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        print("Task save method called")
        if self.pk:
            old_task = Task.objects.get(pk=self.pk)
            print(f"old_task.status: {old_task.status}, self.status: {self.status}")
            if old_task.status != self.status:
                self.last_status = old_task.status
                print(f"self.last_status: {self.last_status}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'task_manager_task'
        ordering = ['-created_at']
        unique_together = ('title', 'deadline', 'owner')

    def __str__(self):
        return self.title


class SubTask(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')

    class Meta:
        db_table = 'subtask_manager_subtask'
        ordering = ['-created_at']
        unique_together = ('title', 'deadline', 'owner')

    def __str__(self):
        return self.title

