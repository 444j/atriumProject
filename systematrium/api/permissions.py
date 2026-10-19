from rest_framework import permissions

class IsAdminOnly(permissions.BasePermission):
    """
    Tanging ang bagong 'ADMIN' (Superuser) ang pinapayagan.
    Para sa full system control at user management.
    """
    def has_permission(self, request, view):
        role = getattr(request.user, 'role', None)
        return (
            request.user and 
            request.user.is_authenticated and 
            role and role.upper() == 'ADMIN'
        )

class IsConsultantOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        role = getattr(request.user, 'role', None)
        # Ensure this matches the exact string in your database (e.g., 'CONSULTANT')
        return (
            request.user and 
            request.user.is_authenticated and 
            role and role.upper() == 'CONSULTANT'
        )

class IsOperatorOnly(permissions.BasePermission):
    """
    Para sa CRUD ng Flights, Hotels, at Tours.
    Pinapayagan ang OPERATOR at ang ADMIN.
    """
    def has_permission(self, request, view):
        role = getattr(request.user, 'role', None)
        return (
            request.user and 
            request.user.is_authenticated and 
            role and role.upper() in ['OPERATOR', 'ADMIN']
        )