from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsSuperAdmin(permissions.BasePermission):
    """Allows access only to superadmin """
    message = "Only Super User is authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == 'SUPER_ADMIN')


class IsHybridAdmin(permissions.BasePermission):
    """Allows access only to hybrid admin users. """
    message = "Only Hybrid Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == 'HYBRID_ADMIN')


class IsTmsAdmin(permissions.BasePermission):
    """Allows access only to TMS Admin users"""
    message = "Only Hybrid Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == "TMS_ADMIN")


class IsAmsAdmin(permissions.BasePermission):
    """Allows access only to TMS Admin users"""
    message = "Only Hybrid Admins are authorized to perform this action."

    def has_permission(self, request, view):
        return bool(request.user.is_authenticated and request.user.role == "AMS_ADMIN")


class IsHybridUserOrReadOnly(permissions.BasePermission):
    """Allows view access only to non admins
     # Check permissions for read-only request"""
    message = "Permission denied"

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role is not None:
            return bool(request.method in SAFE_METHODS or request.user.role == 'HYBRID_USER')
        return False


class IsTmsUserOrReadOnly(permissions.BasePermission):
    """Allows view access only to non admins
    Check permissions for read-only request"""
    message = "Permission denied"

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role is not None:
            return bool(request.method in SAFE_METHODS or request.user.role == 'TMS_USER')
        return False


class IsAmsUserOrReadOnly(permissions.BasePermission):
    """Allows view access only to non admins
     Check permissions for read-only request"""
    message = "Permission denied"

    def has_permission(self, request, view):
        if request.user.is_authenticated and request.user.role is not None:
            return bool(request.method in SAFE_METHODS or request.user.role == 'AMS_USER')
        return False