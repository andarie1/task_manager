from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.timezone import now
from django.db.models import Count
from rest_framework.pagination import PageNumberPagination
from .models import Task, Category, SubTask
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    CategoryCreateSerializer,
    TaskDetailSerializer,
    SubTaskSerializer
)


# Пагинация для всех списков
class DefaultPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


# Словарь дней недели
DAYS_OF_WEEK = {
    "воскресенье": 1,
    "понедельник": 2,
    "вторник": 3,
    "среда": 4,
    "четверг": 5,
    "пятница": 6,
    "суббота": 7,
}


# ✅ Список задач с фильтром по дню недели + пагинация
class TaskListCreateView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        day = self.request.query_params.get('day', '').lower()
        if day in DAYS_OF_WEEK:
            return Task.objects.filter(created_at__week_day=DAYS_OF_WEEK[day])
        return Task.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(
            {"message": "Task created successfully", "task_id": task.id},
            status=status.HTTP_201_CREATED
        )


# ✅ Детали задачи с подзадачами
class TaskDetailView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    lookup_field = 'id'


# ✅ Создание категории
class CategoryCreateView(generics.CreateAPIView):
    serializer_class = CategoryCreateSerializer
    queryset = Category.objects.all()


# ✅ Обновление категории (PUT)
class CategoryUpdateView(generics.UpdateAPIView):
    serializer_class = CategoryCreateSerializer
    queryset = Category.objects.all()
    lookup_field = 'id'
    http_method_names = ['put']


# ✅ Статистика по задачам
class TaskStatisticsView(APIView):
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


# ✅ Список подзадач с пагинацией
class SubTaskListView(generics.ListAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = SubTask.objects.all()
        task_name = self.request.query_params.get('task_name')
        status = self.request.query_params.get('status')

        if task_name:
            queryset = queryset.filter(task__name__icontains=task_name)
        if status:
            queryset = queryset.filter(status=status)
        return queryset
