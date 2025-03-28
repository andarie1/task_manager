from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TaskListCreateView,
    TaskRetrieveUpdateDestroyAPIView,
    TaskDetailView,
    TaskStatisticsView,
    SubTaskListCreateView,
    SubTaskDetailUpdateDeleteView,
    CategoryViewSet
)

# ✅ Создаем роутер и регистрируем ViewSet
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    # 🔹 Task маршруты
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<int:pk>/', TaskRetrieveUpdateDestroyAPIView.as_view(), name='task-detail-update-delete'),
    path('tasks/detail/<int:id>/', TaskDetailView.as_view(), name='task-detail'),
    path('tasks/statistics/', TaskStatisticsView.as_view(), name='task-statistics'),

    # 🔹 SubTask маршруты
    path('subtasks/', SubTaskListCreateView.as_view(), name='subtask-list-create'),
    path('subtasks/<int:id>/', SubTaskDetailUpdateDeleteView.as_view(), name='subtask-detail-update-delete'),

    # 🔹 Category маршруты (CRUD через ViewSet)
    path('', include(router.urls)),
]

