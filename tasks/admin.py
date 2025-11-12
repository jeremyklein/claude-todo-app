from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Task, TaskCompletion, Note


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_preview', 'task_count', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']

    def color_preview(self, obj):
        return format_html(
            '<div style="width: 30px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_preview.short_description = 'Color'

    def task_count(self, obj):
        return obj.tasks.count()
    task_count.short_description = 'Tasks'


class NoteInline(admin.TabularInline):
    model = Note
    extra = 1
    fields = ['content', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'priority_badge', 'category', 'effort_points',
                    'user', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'category', 'llm_suggested', 'llm_automatable',
                   'created_at', 'due_date']
    search_fields = ['title', 'description', 'tags']
    readonly_fields = ['created_at', 'updated_at', 'completed_at']
    date_hierarchy = 'created_at'
    inlines = [NoteInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'user', 'category', 'tags')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'effort_points')
        }),
        ('Dates', {
            'fields': ('due_date', 'created_at', 'updated_at', 'completed_at')
        }),
        ('LLM Integration', {
            'fields': ('llm_suggested', 'llm_automatable', 'llm_metadata'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_completed', 'mark_as_in_progress', 'mark_as_todo']

    def priority_badge(self, obj):
        color = obj.get_priority_display_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'

    def mark_as_completed(self, request, queryset):
        for task in queryset:
            task.mark_completed()
        self.message_user(request, f'{queryset.count()} task(s) marked as completed.')
    mark_as_completed.short_description = 'Mark selected tasks as completed'

    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
        self.message_user(request, f'{queryset.count()} task(s) marked as in progress.')
    mark_as_in_progress.short_description = 'Mark selected tasks as in progress'

    def mark_as_todo(self, request, queryset):
        queryset.update(status='todo', completed_at=None)
        self.message_user(request, f'{queryset.count()} task(s) marked as todo.')
    mark_as_todo.short_description = 'Mark selected tasks as todo'


@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'effort_points', 'completed_at']
    list_filter = ['user', 'completed_at']
    search_fields = ['task__title', 'user__username']
    readonly_fields = ['task', 'user', 'effort_points', 'completed_at']
    date_hierarchy = 'completed_at'

    def has_add_permission(self, request):
        # Task completions should be created automatically
        return False


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'content_preview', 'created_at']
    list_filter = ['created_at', 'user']
    search_fields = ['content', 'task__title']
    readonly_fields = ['created_at']

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'
