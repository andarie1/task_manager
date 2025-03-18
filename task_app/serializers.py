from django.utils import timezone
from rest_framework import serializers
from .models import Task, SubTask, Category

### TASK
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TaskCreateSerializer(serializers.ModelSerializer):
    deadline = serializers.DateTimeField(required=False, allow_null=True)
    categories = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Category.objects.all(), required=False
    )

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'deadline', 'categories']

    def validate_deadline(self, value):
        if value and value < timezone.now():
            raise serializers.ValidationError("Deadline не может быть в прошлом.")
        return value


### CATEGORY
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


### SUBTASK
class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['id', 'title', 'description', 'status', 'deadline', 'task', 'created_at']
        read_only_fields = ['created_at']

class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'subtasks']
