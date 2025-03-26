from django.db.models import Count
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Task, Category, SubTask
from .serializers import TaskSerializer, TaskCreateSerializer, TaskDetailSerializer, CategorySerializer, SubTaskSerializer
from .pagination import DefaultPagination

DAYS_OF_WEEK = {"воскресенье": 1, "понедельник": 2, "вторник": 3, "среда": 4, "четверг": 5, "пятница": 6, "суббота": 7}

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
        return queryset.filter(created_at__week_day=DAYS_OF_WEEK[day]) if day in DAYS_OF_WEEK else queryset

    def create(self, request, *args, **kwargs):
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response({"message": "Task created successfully", "task_id": task.id}, status=status.HTTP_201_CREATED)


class TaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskCreateSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = TaskCreateSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Task updated successfully", "task_id": instance.id}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response({"message": "Task deleted successfully", "task_id": instance.id}, status=status.HTTP_200_OK)


class TaskDetailView(generics.RetrieveAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    lookup_field = 'id'


class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(is_deleted=False) if self.request.query_params.get('show_deleted') != 'true' else Category.objects.all()

    @action(detail=True, methods=['post'])
    def soft_delete(self, request, pk=None):
        category = Category.objects.filter(pk=pk, is_deleted=False).first()
        if category:
            category.soft_delete()
            return Response({"message": "Category soft deleted successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Category not found or already deleted"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        category = Category.objects.filter(pk=pk, is_deleted=True).first()
        if category:
            category.restore()
            return Response({"message": "Category restored successfully"}, status=status.HTTP_200_OK)
        return Response({"error": "Category not found or already active"}, status=status.HTTP_404_NOT_FOUND)


class TaskStatisticsView(generics.GenericAPIView):
    def get(self, request):
        total_tasks = Task.objects.count()
        status_counts = {item['status']: item['count'] for item in Task.objects.values('status').annotate(count=Count('status'))}
        overdue_tasks = Task.objects.filter(deadline__lt=now(), status__in=['new', 'in_progress', 'pending']).count()
        return Response({"total_tasks": total_tasks, "status_counts": status_counts, "overdue_tasks": overdue_tasks})


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
        queryset = super().get_queryset()
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
        return Response({"message": "Subtask created successfully", "subtask_id": subtask.id}, status=status.HTTP_201_CREATED)


class SubTaskDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    lookup_field = 'id'

    def update(self, request, *args, **kwargs):
        subtask = self.get_object()
        serializer = self.get_serializer(subtask, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Subtask updated successfully", "subtask_id": subtask.id}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"message": "Subtask deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
