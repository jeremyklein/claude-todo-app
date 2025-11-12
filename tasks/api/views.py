"""
API Views for Django REST Framework
Provides ViewSets and APIViews for all endpoints
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter

from tasks.models import Task, Category, TaskCompletion, Note
from .serializers import (
    TaskSerializer, TaskListSerializer, TaskCreateSerializer, TaskCompleteSerializer,
    CategorySerializer, NoteSerializer, DashboardSerializer, EffortPointsSerializer,
    CategoryBreakdownSerializer, CompletionHistorySerializer
)
from .permissions import IsTaskOwner, IsNoteOwner
from .filters import TaskFilter, CategoryFilter


@extend_schema_view(
    list=extend_schema(description="List all tasks for the authenticated user"),
    create=extend_schema(description="Create a new task"),
    retrieve=extend_schema(description="Get a specific task by ID"),
    update=extend_schema(description="Update a task"),
    partial_update=extend_schema(description="Partially update a task"),
    destroy=extend_schema(description="Delete a task"),
)
class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task model
    Provides CRUD operations and custom actions
    """
    permission_classes = [IsAuthenticated, IsTaskOwner]
    filter_class = TaskFilter
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'updated_at', 'due_date', 'priority', 'effort_points']
    ordering = ['-priority', 'due_date']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'list':
            return TaskListSerializer
        elif self.action == 'create':
            return TaskCreateSerializer
        return TaskSerializer

    def get_queryset(self):
        """Return tasks for the authenticated user only"""
        return Task.objects.filter(user=self.request.user).select_related('category').prefetch_related('notes')

    def perform_create(self, serializer):
        """Set the user when creating a task"""
        serializer.save(user=self.request.user)

    @extend_schema(
        request=None,
        responses={200: TaskCompleteSerializer},
        description="Mark a task as completed and record effort points"
    )
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """
        Custom action to mark a task as completed
        """
        task = self.get_object()

        if task.status == 'completed':
            return Response(
                {'message': f'Task "{task.title}" is already completed.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.mark_completed()

        serializer = TaskCompleteSerializer(data={
            'message': f'Task "{task.title}" completed! Earned {task.effort_points} effort points.',
            'task_id': task.id,
            'effort_points': task.effort_points
        })
        serializer.is_valid()

        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='q',
                description='Search query for title, description, or tags',
                required=True,
                type=str
            )
        ],
        responses={200: TaskListSerializer(many=True)},
        description="Search tasks by text in title, description, or tags"
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Custom action to search tasks
        """
        query = request.query_params.get('q', '')

        if not query:
            return Response(
                {'error': 'Search query parameter "q" is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tasks = self.get_queryset().filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )

        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description="List all categories"),
    create=extend_schema(description="Create a new category"),
    retrieve=extend_schema(description="Get a specific category by ID"),
    update=extend_schema(description="Update a category"),
    partial_update=extend_schema(description="Partially update a category"),
    destroy=extend_schema(description="Delete a category"),
)
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Category model
    Provides CRUD operations for categories
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    filter_class = CategoryFilter
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']

    @extend_schema(
        responses={200: TaskListSerializer(many=True)},
        description="Get all tasks in this category for the authenticated user"
    )
    @action(detail=True, methods=['get'])
    def tasks(self, request, pk=None):
        """
        Custom action to get all tasks in a category
        """
        category = self.get_object()
        tasks = Task.objects.filter(category=category, user=request.user)
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(description="List notes for a task"),
    create=extend_schema(description="Add a note to a task"),
    retrieve=extend_schema(description="Get a specific note"),
    update=extend_schema(description="Update a note"),
    partial_update=extend_schema(description="Partially update a note"),
    destroy=extend_schema(description="Delete a note"),
)
class NoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Note model
    Provides CRUD operations for notes
    """
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsNoteOwner]

    def get_queryset(self):
        """Return notes for the authenticated user only"""
        return Note.objects.filter(user=self.request.user).select_related('task')

    def perform_create(self, serializer):
        """Set the user when creating a note"""
        # Ensure the task belongs to the user
        task_id = self.request.data.get('task')
        task = Task.objects.filter(id=task_id, user=self.request.user).first()

        if not task:
            raise PermissionError("Cannot add note to task that doesn't belong to you")

        serializer.save(user=self.request.user)


class DashboardAPIView(APIView):
    """
    API view for dashboard data
    Returns overview of tasks and effort points
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: DashboardSerializer},
        description="Get dashboard overview with stats, upcoming tasks, and overdue tasks"
    )
    def get(self, request):
        """Return dashboard data for the authenticated user"""
        user = request.user
        today = timezone.now().date()

        # Get task counts
        tasks_todo = Task.objects.filter(user=user, status='todo').count()
        tasks_in_progress = Task.objects.filter(user=user, status='in_progress').count()
        tasks_completed_today = Task.objects.filter(
            user=user,
            status='completed',
            completed_at__date=today
        ).count()

        # Get effort points
        points_today = TaskCompletion.get_daily_points(user, today)
        points_week = TaskCompletion.get_weekly_points(user, today)
        points_month = TaskCompletion.get_monthly_points(user, today)
        points_year = TaskCompletion.get_yearly_points(user, today)

        # Get upcoming tasks (due in next 7 days)
        upcoming_deadline = today + timedelta(days=7)
        upcoming_tasks = Task.objects.filter(
            user=user,
            status__in=['todo', 'in_progress'],
            due_date__gte=today,
            due_date__lte=upcoming_deadline
        ).order_by('due_date')

        # Get overdue tasks
        overdue_tasks = Task.objects.filter(
            user=user,
            status__in=['todo', 'in_progress'],
            due_date__lt=today
        ).order_by('due_date')

        data = {
            'effort_points': {
                'today': points_today,
                'this_week': points_week,
                'this_month': points_month,
                'this_year': points_year
            },
            'task_counts': {
                'todo': tasks_todo,
                'in_progress': tasks_in_progress,
                'completed_today': tasks_completed_today
            },
            'upcoming_tasks': upcoming_tasks,
            'overdue_tasks': overdue_tasks
        }

        serializer = DashboardSerializer(data)
        return Response(serializer.data)


class EffortPointsAPIView(APIView):
    """
    API view for effort points analytics
    Returns effort points by time period
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='period',
                description='Time period: today, week, month, year, or all',
                required=False,
                type=str,
                enum=['today', 'week', 'month', 'year', 'all']
            )
        ],
        responses={200: EffortPointsSerializer},
        description="Get effort points and task analytics for specified period"
    )
    def get(self, request):
        """Return effort points analytics for the authenticated user"""
        user = request.user
        today = date.today()
        period = request.query_params.get('period', 'all')

        result = {
            'period': period,
            'total_tasks': Task.objects.filter(user=user).count(),
            'completed_tasks': Task.objects.filter(user=user, status='completed').count(),
        }

        if period in ['today', 'all']:
            result['points_today'] = TaskCompletion.get_daily_points(user, today)

        if period in ['week', 'all']:
            result['points_this_week'] = TaskCompletion.get_weekly_points(user, today)

        if period in ['month', 'all']:
            result['points_this_month'] = TaskCompletion.get_monthly_points(user, today)

        if period in ['year', 'all']:
            result['points_this_year'] = TaskCompletion.get_yearly_points(user, today)

        if period == 'all':
            result['total_points_earned'] = TaskCompletion.objects.filter(user=user).aggregate(
                total=Sum('effort_points')
            )['total'] or 0

            # Category breakdown
            category_stats = TaskCompletion.objects.filter(user=user).values(
                'task__category__name'
            ).annotate(
                total_points=Sum('effort_points'),
                task_count=Count('id')
            ).order_by('-total_points')

            result['category_breakdown'] = list(category_stats)

        serializer = EffortPointsSerializer(result)
        return Response(serializer.data)


class CategoryBreakdownAPIView(APIView):
    """
    API view for category breakdown analytics
    Returns effort points and task counts by category
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: CategoryBreakdownSerializer(many=True)},
        description="Get effort points breakdown by category"
    )
    def get(self, request):
        """Return category breakdown for the authenticated user"""
        user = request.user

        category_stats = TaskCompletion.objects.filter(user=user).values(
            'task__category__name'
        ).annotate(
            total_points=Sum('effort_points'),
            task_count=Count('id')
        ).order_by('-total_points')

        serializer = CategoryBreakdownSerializer(category_stats, many=True)
        return Response(serializer.data)


class CompletionHistoryAPIView(APIView):
    """
    API view for task completion history
    Returns recent task completions
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='limit',
                description='Number of completions to return (default: 10)',
                required=False,
                type=int
            )
        ],
        responses={200: CompletionHistorySerializer(many=True)},
        description="Get recent task completions"
    )
    def get(self, request):
        """Return recent completions for the authenticated user"""
        user = request.user
        limit = int(request.query_params.get('limit', 10))

        completions = TaskCompletion.objects.filter(user=user).select_related(
            'task', 'task__category'
        ).order_by('-completed_at')[:limit]

        serializer = CompletionHistorySerializer(completions, many=True)
        return Response(serializer.data)
