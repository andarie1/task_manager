from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from django.db.models import Count
from .models import Task, Category
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    CategoryCreateSerializer, TaskDetailSerializer
)


@api_view(["GET", "POST"])
def tasks_list_create(request):
    """
    GET: Получить список всех задач.
    POST: Создать новую задачу.
    """
    if request.method == "GET":
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == "POST":
        serializer = TaskCreateSerializer(data=request.data)
        if serializer.is_valid():
            task = serializer.save()
            return Response(
                {"message": "Task created successfully", "task_id": task.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def task_detail(request, task_id):
    """
    GET: Получить детальную информацию о задаче по ID.
    """
    try:
        task = Task.objects.get(id=task_id)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
def category_create(request):
    """
    POST: Создать новую категорию.
    """
    serializer = CategoryCreateSerializer(data=request.data)
    if serializer.is_valid():
        category = serializer.save()
        return Response(CategoryCreateSerializer(category).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def category_update(request, id):
    """
    PUT: Обновить данные категории по ID (частичное обновление).
    """
    try:
        category = Category.objects.get(id=id)
    except Category.DoesNotExist:
        return Response({'error': 'Категория не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = CategoryCreateSerializer(category, data=request.data, partial=True)
    if serializer.is_valid():
        category = serializer.save()
        return Response(CategoryCreateSerializer(category).data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def task_statistics(request):
    """
    GET: Получить статистику по задачам:
    - Общее количество задач.
    - Количество задач по статусам.
    - Количество просроченных задач.
    """
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
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def task_detail(request, id):
    """
    Получение одной задачи с вложенными подзадачами.
    """
    try:
        task = Task.objects.get(id=id)
    except Task.DoesNotExist:
        return Response({'error': 'Задача не найдена.'}, status=status.HTTP_404_NOT_FOUND)

    serializer = TaskDetailSerializer(task)
    return Response(serializer.data, status=status.HTTP_200_OK)