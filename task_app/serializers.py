from django.template.defaultfilters import title
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Task, SubTask, Category

### TASK
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'deadline']

class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

### CATEGORY
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','name']

class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

    def create(self, validated_data):
        title = validated_data.get('title')

        if Category.objects.filter(title=title).exists():
            raise ValidationError(f'Категория с названием "{title}" уже существует.')

        category = Category.objects.create(**validated_data)
        return category

    def update(self, instance, validated_data):
        new_title = validated_data.get('title', instance.title)

        if Category.objects.filter(title=new_title).exclude(id=instance.id).exists():
            raise ValidationError(f'Категория с названием "{new_title}" уже существует.')

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
