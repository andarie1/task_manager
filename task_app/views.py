from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status, filters, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Task, Category, SubTask
from .serializers import (
    TaskCreateSerializer, TaskDetailSerializer, CategorySerializer, SubTaskSerializer, TaskSerializer,
    CustomTokenObtainPairSerializer
)
from .pagination import DefaultPagination
from .permissions import IsOwnerOrReadOnly
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "message": "User registered successfully",
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }, status=status.HTTP_201_CREATED)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Выход выполнен"}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


DAYS_OF_WEEK = {"воскресенье": 1, "понедельник": 2, "вторник": 3, "среда": 4, "четверг": 5, "пятница": 6, "суббота": 7}

class TaskListCreateView(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class TaskRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskDetailSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_object(self):
        task_id = self.kwargs.get("pk")

        if not task_id:
            raise NotFound({"detail": "Task ID is missing in URL."})

        obj = get_object_or_404(Task, id=task_id)
        self.check_object_permissions(self.request, obj)
        return obj

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        total_tasks = Task.objects.filter(owner=request.user).count()
        status_counts = {
            item['status']: item['count'] for item in Task.objects.filter(owner=request.user)
            .values('status').annotate(count=Count('status'))
        }
        overdue_tasks = Task.objects.filter(
            owner=request.user, deadline__lt=now(), status__in=['new', 'in_progress', 'pending']
        ).count()
        return Response({"total_tasks": total_tasks, "status_counts": status_counts, "overdue_tasks": overdue_tasks})


class SubTaskListCreateView(generics.ListCreateAPIView):
    serializer_class = SubTaskSerializer
    pagination_class = DefaultPagination
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'deadline']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at']
    ordering = ['created_at']

    def get_queryset(self):
        queryset = SubTask.objects.filter(owner=self.request.user)
        task_name = self.request.query_params.get('task_name')
        subtask_status = self.request.query_params.get('status')
        if task_name:
            queryset = queryset.filter(task__title__icontains=task_name)
        if subtask_status:
            queryset = queryset.filter(status=subtask_status)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class SubTaskDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubTask.objects.all()
    serializer_class = SubTaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return SubTask.objects.filter(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        subtask = self.get_object()
        serializer = self.get_serializer(subtask, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Subtask updated successfully", "subtask_id": subtask.id}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response({"message": "Subtask deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

