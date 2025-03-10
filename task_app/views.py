from rest_framework import generics, status
from rest_framework.response import Response
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


# ✅ Список задач с фильтром по дню недели
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

    def get_queryset(self):
        queryset = SubTask.objects.all()
        task_name = self.request.query_params.get('task_name')
        subtask_status = self.request.query_params.get('status')
        if task_name and subtask_status:
            queryset = queryset.filter(
                task__name__icontains=task_name,
                status=subtask_status
            )
        elif task_name:
            queryset = queryset.filter(task__name__icontains=task_name)
        elif subtask_status:
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


# ✅ Единый класс: Получение, обновление, удаление подзадачи (без дублирования)
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
        return Response({"message": "Subtask deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
