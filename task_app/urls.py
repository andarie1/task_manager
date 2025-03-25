from django.urls import path
from .views import (
    tasks_list_create,
    task_detail,
    category_create,
    category_update,
    task_statistics
)

urlpatterns = [
    # Получение списка задач и создание новой задачи
    path("tasks/", tasks_list_create, name="task-list-create"),

    # Получение детальной информации о задаче по ID
    path("tasks/<int:task_id>/", task_detail, name="task-detail"),

    # Создание новой категории
    path('categories/create/', category_create, name='category-create'),

    # Обновление категории по ID
    path('categories/<int:id>/update/', category_update, name='category-update'),

    # Получение статистики по задачам
    path('tasks/statistics/', task_statistics, name="task-statistics"),
]



