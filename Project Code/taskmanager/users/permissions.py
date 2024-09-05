from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """
    Allows access only to admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='admin').exists()

class IsRegularUser(BasePermission):
    """
    Allows access only to regular users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.groups.filter(name='regular').exists()
