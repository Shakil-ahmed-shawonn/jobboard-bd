"""
accounts/views.py

Registration is public (AllowAny). Login/token refresh are handled by
SimpleJWT's built-in views, wired directly in jobboard/urls.py.
"""

from rest_framework import generics, permissions

from .serializers import MeSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
    """POST /api/accounts/register/ — creates a User (+ CompanyProfile if employer)."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    """GET /api/accounts/me/ — returns the logged-in user's id/username/role.
    Called by the frontend right after login to determine dashboard routing."""

    serializer_class = MeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
