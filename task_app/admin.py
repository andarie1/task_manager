from django.contrib import admin
from .models import Category, Task, SubTask

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 1
    min_num = 0
    can_delete = True

@admin.action(description="Mark as 'Done'")
def mark_as_done(self, request, queryset):
    queryset.update(status="done")

@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'task', 'status', 'deadline')
    list_filter = ('status',)
    search_fields = ('title', 'description')
    actions = [mark_as_done]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'deadline', 'created_at')
    list_filter = ('status', 'deadline')
    search_fields = ('title', 'description')
    inlines = [SubTaskInline]





