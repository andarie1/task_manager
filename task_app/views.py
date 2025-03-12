from django.db.models import Count
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Task, Category, SubTask
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskDetailSerializer, CategoryCreateSerializer, SubTaskSerializer
)


# ✅ Универсальная пагинация
class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# ✅ Словарь дней недели
DAYS_OF_WEEK = {
    "воскресенье": 1,
    "понедельник": 2,
    "вторник": 3,
    "среда": 4,
    "четверг": 5,
    "пятница": 6,
    "суббота": 7,
}


# ✅ Список и создание задач + фильтрация по дню недели
class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        day = self.request.query_params.get('day', '').lower()
        if day in DAYS_OF_WEEK:
            queryset = queryset.filter(created_at__week_day=DAYS_OF_WEEK[day])
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(
            {"message": "Task created successfully", "task_id": task.id},
            status=status.HTTP_201_CREATED
        )


# ✅ Получение, обновление, удаление задачи
class TaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer  # Можно оставить или использовать TaskSerializer для разных целей

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TaskCreateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Task updated successfully", "task_id": instance.id},
            status=status.HTTP_200_OK
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"message": "Task deleted successfully", "task_id": instance.id},
            status=status.HTTP_200_OK
        )


# ✅ Детали задачи с подзадачами
class TaskDetailView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    lookup_field = 'id'


# ✅ Получение/Создание категории
class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryCreateSerializer
    pagination_class = DefaultPagination

class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategoryCreateSerializer
    queryset = Category.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = CategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return Response(
            {"message": "Category created successfully", "category_id": category.id},
            status=status.HTTP_201_CREATED
        )


# ✅ Обновление категории
class CategoryUpdateView(generics.UpdateAPIView):
    serializer_class = CategoryCreateSerializer
    queryset = Category.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']

    def update(self, request, *args, **kwargs):
        serializer = CategoryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = serializer.save()
        return Response(
            {"message": "Category updated successfully", "category_id": category.id},
            status=status.HTTP_200_OK
        )

# ✅ Статистика по задачам
class TaskStatisticsView(generics.GenericAPIView):
    def get(self, request):
        total_tasks = Task.objects.count()
        status_counts = Task.objects.values('status').annotate(count=Count('status'))
        overdue_tasks = Task.objects.filter(
            deadline__lt=now(),
            status__in=['new', 'in_progress', 'pending']
        ).count()

        return Response({
            "total_tasks": total_tasks,
            "status_counts": {item['status']: item['count'] for item in status_counts},
            "overdue_tasks": overdue_tasks
        })


# ✅ Единый класс: Список + создание подзадач (без дублирования)
class SubTaskListCreateView(generics.ListCreateAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    pagination_class = DefaultPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_queryset(self):
        queryset = SubTask.objects.all()
        task_name = self.request.query_params.get('task_name')
        subtask_status = self.request.query_params.get('status')

        if task_name:
            queryset = queryset.filter(task__title__icontains=task_name)
        if subtask_status:
            queryset = queryset.filter(status=subtask_status)

        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subtask = serializer.save()
        return Response(
            {"message": "Subtask created successfully", "subtask_id": subtask.id},
            status=status.HTTP_201_CREATED
        )


# ✅ Детальный просмотр, обновление, удаление подзадачи
class SubTaskDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        subtask = self.get_object()
        serializer = self.get_serializer(subtask)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        subtask = self.get_object()
        serializer = self.get_serializer(subtask, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"message": "Subtask updated successfully", "subtask_id": subtask.id},
            status=status.HTTP_200_OK
        )

    def destroy(self, request, *args, **kwargs):
        subtask = self.get_object()
        subtask.delete()
        return Response(
            {"message": "Subtask deleted successfully"},
            status=status.HTTP_204_NO_CONTENT
        )