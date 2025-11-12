"""
URL routing for Django REST Framework API
Defines all API endpoints
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    TaskViewSet, CategoryViewSet, NoteViewSet,
    DashboardAPIView, EffortPointsAPIView,
    CategoryBreakdownAPIView, CompletionHistoryAPIView
)

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'notes', NoteViewSet, basename='note')

# Define URL patterns
urlpatterns = [
    # Authentication endpoints
    path('auth/token/', obtain_auth_token, name='api_token_auth'),

    # Analytics endpoints
    path('analytics/dashboard/', DashboardAPIView.as_view(), name='analytics-dashboard'),
    path('analytics/effort-points/', EffortPointsAPIView.as_view(), name='analytics-effort-points'),
    path('analytics/category-breakdown/', CategoryBreakdownAPIView.as_view(), name='analytics-category-breakdown'),
    path('analytics/completion-history/', CompletionHistoryAPIView.as_view(), name='analytics-completion-history'),

    # Router URLs (includes tasks, categories, notes)
    path('', include(router.urls)),
]
