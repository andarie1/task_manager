from django.urls import path
from .views import tasks_list_create, task_detail, category_create, task_statistics

urlpatterns = [
    path("tasks/", tasks_list_create, name="task-list-create"),
    path("tasks/<int:task_id>/", task_detail, name="task-detail"),
    path('categories/', category_create, name="category-create"),
    path('tasks/statistics/', task_statistics, name="task-statistics"),
]


