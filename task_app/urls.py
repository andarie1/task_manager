from django.urls import path
from .views import (
    TaskListCreateView,
    TaskDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    TaskStatisticsView,
    SubTaskListCreateView,
    SubTaskDetailUpdateDeleteView
)

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:id>/', TaskDetailView.as_view(), name='task-detail'),
    path('categories/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:id>/', CategoryUpdateView.as_view(), name='category-update'),
    path('tasks/statistics/', TaskStatisticsView.as_view(), name='task-statistics'),
    path('subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:id>/', SubTaskDetailUpdateDeleteView.as_view(), name='subtask-detail-update-delete'),
]

