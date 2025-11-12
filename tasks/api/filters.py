"""
Custom filters for Django REST Framework API
Provides advanced filtering capabilities for tasks
"""

import django_filters
from tasks.models import Task, Category


class TaskFilter(django_filters.FilterSet):
    """
    Filter set for Task model
    Provides filtering by status, priority, category, due dates, and tags
    """

    # Exact match filters
    status = django_filters.ChoiceFilter(choices=Task.STATUS_CHOICES)
    priority = django_filters.ChoiceFilter(choices=Task.PRIORITY_CHOICES)

    # Category filter (by name, case-insensitive)
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='iexact')

    # Date range filters
    due_date_gte = django_filters.DateFilter(field_name='due_date', lookup_expr='gte', label='Due date from')
    due_date_lte = django_filters.DateFilter(field_name='due_date', lookup_expr='lte', label='Due date to')
    due_date = django_filters.DateFilter(field_name='due_date', lookup_expr='exact', label='Due date')

    # Created date range
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    # Tags filter (contains)
    tags_contains = django_filters.CharFilter(field_name='tags', lookup_expr='icontains', label='Tags contain')

    # Boolean filters
    llm_suggested = django_filters.BooleanFilter(field_name='llm_suggested')
    llm_automatable = django_filters.BooleanFilter(field_name='llm_automatable')

    # Effort points range
    effort_points_min = django_filters.NumberFilter(field_name='effort_points', lookup_expr='gte')
    effort_points_max = django_filters.NumberFilter(field_name='effort_points', lookup_expr='lte')

    class Meta:
        model = Task
        fields = [
            'status',
            'priority',
            'category',
            'due_date',
            'due_date_gte',
            'due_date_lte',
            'created_after',
            'created_before',
            'tags_contains',
            'llm_suggested',
            'llm_automatable',
            'effort_points_min',
            'effort_points_max',
        ]


class CategoryFilter(django_filters.FilterSet):
    """
    Filter set for Category model
    Provides basic filtering by name
    """

    name = django_filters.CharFilter(lookup_expr='icontains', label='Name contains')

    class Meta:
        model = Category
        fields = ['name']
