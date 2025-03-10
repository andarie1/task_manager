from django.template.defaultfilters import title
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Task, SubTask, Category

### TASK
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

    def validate_deadline(self, value):
        if value < timezone.now():
            raise serializers.ValidationError("Deadline не может быть в прошлом")
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

    def create(self, validated_data):
        name = validated_data.get('name')

        if Category.objects.filter(name).exists():
            raise ValidationError(f'Категория с названием "{name}" уже существует.')

        category = Category.objects.create(**validated_data)
        return category

    def update(self, instance, validated_data):
        new_name = validated_data.get('name', instance.name).title()

        if Category.objects.filter(name=new_name).exclude(id=instance.id).exists():
            raise ValidationError(f'Категория с названием "{new_name}" уже существует.')

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

### SUBTASK
class SubTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubTask
        fields = ['title', 'description', 'status', 'deadline']
        read_only_fields = ['created_at']

class TaskDetailSerializer(serializers.ModelSerializer):
    subtasks = SubTaskSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'subtasks']
