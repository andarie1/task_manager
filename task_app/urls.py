from django.urls import path
from .views import (
    TaskListCreateView,
    TaskDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    TaskStatisticsView,
    SubTaskListView
)

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:id>/', TaskDetailView.as_view(), name='task-detail'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:id>/update/', CategoryUpdateView.as_view(), name='category-update'),
    path('tasks/statistics/', TaskStatisticsView.as_view(), name='task-statistics'),
    path('subtasks/', SubTaskListView.as_view(), name='subtask-list'),
]
