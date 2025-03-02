from django.urls import path
from .views import tasks_list_create, task_detail, task_statistics, category_create, category_update

urlpatterns = [
    path("tasks/", tasks_list_create, name="task-list-create"),
    path("tasks/<int:task_id>/", task_detail, name="task-detail"),
    path('categories/create/', category_create, name='category-create'),
    path('categories/<int:id>/update/', category_update, name='category-update'),
    path('tasks/statistics/', task_statistics, name="task-statistics"),
    path('/tasks/<int:id>/', task_detail, name='task-detail'),
]


