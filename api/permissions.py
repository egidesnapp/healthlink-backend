# api/permissions.py

from rest_framework import permissions

class BaseRolePermission(permissions.BasePermission):
    """
    Base permission class to check if a user has a specific role.
    """
    required_role = None

    def has_permission(self, request, view):
        # Allow OPTIONS requests (for CORS preflight)
        if request.method == 'OPTIONS':
            return True

        if not request.user.is_authenticated:
            return False

        # Assuming user.role is a ForeignKey to a Role model that has a 'name' field
        if hasattr(request.user, 'role') and request.user.role:
            return request.user.role.name == self.required_role
        return False

class IsSuperAdmin(BaseRolePermission):
    required_role = 'Admin' # Assuming 'Admin' is the name of your SuperAdmin role

class IsFacilityAdmin(BaseRolePermission):
    required_role = 'Facility Admin' # Assuming 'Facility Admin' is the name of your Facility Admin role

class IsDoctor(BaseRolePermission):
    required_role = 'Doctor' # Assuming 'Doctor' is the name of your Doctor role

class IsNurse(BaseRolePermission):
    required_role = 'Nurse' # Assuming 'Nurse' is the name of your Nurse role

class IsPatient(BaseRolePermission):
    required_role = 'Patient' # Assuming 'Patient' is the name of your Patient role

class IsPharmacist(BaseRolePermission):
    required_role = 'Pharmacist' # Assuming 'Pharmacist' is the name of your Pharmacist role