"""
accounts/permissions.py

Reusable role-checking permission classes for other apps (jobs, applications)
to import. Keeping these here avoids duplicating role logic per app.
Docs: https://www.django-rest-framework.org/api-guide/permissions/
"""

from rest_framework.permissions import BasePermission


class IsEmployer(BasePermission):
    """Allows access only to authenticated users with role='employer'."""

    message = "Only employer accounts can perform this action."

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.is_employer())


class IsSeeker(BasePermission):
    """Allows access only to authenticated users with role='seeker'."""

    message = "Only job seeker accounts can perform this action."

    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated and request.user.is_seeker())
