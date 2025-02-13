from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In progress'),
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    categories = models.ManyToManyField(Category, related_name='tasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('title', 'deadline') # 2 уникальных поля для задачи

    def __str__(self):
        return self.title

class SubTask(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_progress', 'In progress'),
        ('pending', 'Pending'),
        ('blocked', 'Blocked'),
        ('done', 'Done'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='subtasks')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    deadline = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# Категории
categories = [
    Category(name="Работа"),
    Category(name="Учёба"),
    Category(name="Личное")
]

# Задачи
tasks = [
    Task(title="Написать отчёт", description="Создать финальный отчёт для клиента", status="new", deadline="2025-03-01 12:00"),
    Task(title="Подготовиться к экзамену", description="Пройти все тесты и конспекты", status="in_progress", deadline="2025-03-10 18:00"),
    Task(title="Починить кран", description="Вызвать сантехника", status="pending", deadline="2025-02-20 09:00")
]

# Подзадачи
subtasks = [
    SubTask(title="Собрать данные", description="Собрать все исходные данные для отчёта", task=tasks[0], status="new", deadline="2025-02-28 10:00"),
    SubTask(title="Решить пробные тесты", description="Пройти 5 пробных тестов", task=tasks[1], status="in_progress", deadline="2025-03-08 14:00"),
    SubTask(title="Купить новые прокладки", description="Посетить магазин сантехники", task=tasks[2], status="pending", deadline="2025-02-19 16:00")
]
