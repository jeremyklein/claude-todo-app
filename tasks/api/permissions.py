"""
Custom permissions for Django REST Framework API
Ensures users can only access and modify their own data
"""

from rest_framework import permissions


class IsTaskOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a task to view/edit it
    """

    def has_object_permission(self, request, view, obj):
        # Task must belong to the requesting user
        return obj.user == request.user


class IsNoteOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of a note to view/edit it
    """

    def has_object_permission(self, request, view, obj):
        # Note must belong to the requesting user
        return obj.user == request.user


class IsTaskOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to allow read-only access to all, but edit only to owners
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner
        return obj.user == request.user
