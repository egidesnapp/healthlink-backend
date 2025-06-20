
from rest_framework import permissions

class IsSuperAdmin(permissions.BasePermission):
    """
    Custom permission to only allow super admins.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsFacilityAdmin(permissions.BasePermission):
    """
    Custom permission to only allow facility admins.
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role and 
                request.user.role.name == 'Facility Admin')

class IsDoctor(permissions.BasePermission):
    """
    Custom permission to only allow doctors.
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role and 
                request.user.role.name == 'Doctor')

class IsNurse(permissions.BasePermission):
    """
    Custom permission to only allow nurses.
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role and 
                request.user.role.name == 'Nurse')

class IsPharmacist(permissions.BasePermission):
    """
    Custom permission to only allow pharmacists.
    """
    def has_permission(self, request, view):
        return (request.user.is_authenticated and 
                request.user.role and 
                request.user.role.name == 'Pharmacist')
