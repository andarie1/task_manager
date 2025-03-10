from django.db.models import Count
from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Task
from .serializers import TaskCreateSerializer, TaskSerializer, CategorySerializer

@api_view(["GET", "POST"])
def tasks_list_create(request):
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
    try:
        task = Task.objects.get(id=task_id)
        serializer = TaskSerializer(task)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Task.DoesNotExist:
        return Response({"error": "Task not found"}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def category_create(request):
    serializer = CategorySerializer(data=request.data)
    if serializer.is_valid():
        category = serializer.save()
        return Response({"id": category.id, "name": category.name}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def task_statistics(request):
    total_tasks = Task.objects.count()
    status_counts = Task.objects.values('status').annotate(count=Count('status'))
    overdue_tasks = Task.objects.filter(deadline__lt=now(), status__in=['new', 'in_progress', 'pending']).count()

    return Response({
        "total_tasks": total_tasks,
        "status_counts": {item['status']: item['count'] for item in status_counts},
        "overdue_tasks": overdue_tasks
    }, status=status.HTTP_200_OK)