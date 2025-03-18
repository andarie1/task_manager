from django.urls import path
from .views import (
    TaskListCreateView,
    TaskDetailView,
    CategoryCreateView,
    CategoryUpdateView,
    TaskStatisticsView,
    SubTaskListCreateView,
    SubTaskDetailUpdateDeleteView,
    CategoryListView,
    TaskRetrieveUpdateDestroyAPIView
)

urlpatterns = [
    # Task
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyAPIView.as_view(), name='task-detail-update-delete'),
    path('tasks/detail/<int:id>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/statistics/', TaskStatisticsView.as_view(), name='task-statistics'),

    # Category
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category-create'),
    path('categories/<int:id>/update/', CategoryUpdateView.as_view(), name='category-update'),

    # SubTask
    path('subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:id>/', SubTaskDetailUpdateDeleteView.as_view(), name='subtask-detail-update-delete'),
]
