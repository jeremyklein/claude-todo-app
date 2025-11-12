"""
Serializers for Django REST Framework API
Handles serialization/deserialization of model instances to/from JSON
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from tasks.models import Task, Category, TaskCompletion, Note
from datetime import date


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'created_at', 'task_count']
        read_only_fields = ['id', 'created_at', 'task_count']

    def get_task_count(self, obj):
        """Return number of tasks in this category"""
        return obj.tasks.count()


class CategorySimpleSerializer(serializers.ModelSerializer):
    """Simplified category serializer for nested representations"""
    class Meta:
        model = Category
        fields = ['id', 'name', 'color']


class NoteSerializer(serializers.ModelSerializer):
    """Serializer for Note model"""
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Note
        fields = ['id', 'task', 'content', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class TaskSerializer(serializers.ModelSerializer):
    """Full serializer for Task model"""
    category = CategorySimpleSerializer(read_only=True)
    category_name = serializers.CharField(write_only=True, required=False, allow_null=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    notes = NoteSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'category', 'category_name',
            'status', 'status_display', 'priority', 'priority_display',
            'effort_points', 'due_date', 'tags', 'user',
            'created_at', 'updated_at', 'completed_at',
            'llm_suggested', 'llm_automatable', 'llm_metadata',
            'notes'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'completed_at']

    def validate_effort_points(self, value):
        """Validate effort points are between 1 and 10"""
        if value < 1 or value > 10:
            raise serializers.ValidationError("Effort points must be between 1 and 10")
        return value

    def validate_priority(self, value):
        """Validate priority is between 1 and 4"""
        if value < 1 or value > 4:
            raise serializers.ValidationError("Priority must be between 1 and 4")
        return value

    def create(self, validated_data):
        """Create task and handle category by name"""
        category_name = validated_data.pop('category_name', None)

        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)
            validated_data['category'] = category

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Update task and handle category by name"""
        category_name = validated_data.pop('category_name', None)

        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)
            validated_data['category'] = category

        return super().update(instance, validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Lighter serializer for task lists (without notes)"""
    category = CategorySimpleSerializer(read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'category', 'status', 'status_display',
            'priority', 'priority_display', 'effort_points',
            'due_date', 'tags', 'created_at', 'completed_at'
        ]


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks"""
    category_name = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'category_name', 'status',
            'priority', 'effort_points', 'due_date', 'tags',
            'llm_suggested', 'llm_automatable', 'llm_metadata'
        ]

    def validate_effort_points(self, value):
        if value < 1 or value > 10:
            raise serializers.ValidationError("Effort points must be between 1 and 10")
        return value

    def validate_priority(self, value):
        if value < 1 or value > 4:
            raise serializers.ValidationError("Priority must be between 1 and 4")
        return value

    def create(self, validated_data):
        category_name = validated_data.pop('category_name', None)

        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)
            validated_data['category'] = category

        # User will be set in the view
        return Task.objects.create(**validated_data)


class TaskCompleteSerializer(serializers.Serializer):
    """Serializer for marking a task as completed"""
    message = serializers.CharField(read_only=True)
    task_id = serializers.IntegerField(read_only=True)
    effort_points = serializers.IntegerField(read_only=True)


class DashboardSerializer(serializers.Serializer):
    """Serializer for dashboard data"""
    effort_points = serializers.DictField()
    task_counts = serializers.DictField()
    upcoming_tasks = TaskListSerializer(many=True)
    overdue_tasks = TaskListSerializer(many=True)


class EffortPointsSerializer(serializers.Serializer):
    """Serializer for effort points analytics"""
    period = serializers.CharField()
    points_today = serializers.IntegerField(required=False)
    points_this_week = serializers.IntegerField(required=False)
    points_this_month = serializers.IntegerField(required=False)
    points_this_year = serializers.IntegerField(required=False)
    total_points_earned = serializers.IntegerField(required=False)
    total_tasks = serializers.IntegerField(required=False)
    completed_tasks = serializers.IntegerField(required=False)
    category_breakdown = serializers.ListField(required=False)


class CategoryBreakdownSerializer(serializers.Serializer):
    """Serializer for category breakdown analytics"""
    task__category__name = serializers.CharField()
    total_points = serializers.IntegerField()
    task_count = serializers.IntegerField()


class CompletionHistorySerializer(serializers.ModelSerializer):
    """Serializer for task completion history"""
    task_title = serializers.CharField(source='task.title')
    task_id = serializers.IntegerField(source='task.id')
    category = serializers.CharField(source='task.category.name', allow_null=True)
    user = serializers.StringRelatedField()

    class Meta:
        model = TaskCompletion
        fields = ['id', 'task_id', 'task_title', 'category', 'user', 'effort_points', 'completed_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model (for registration/profile)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']
