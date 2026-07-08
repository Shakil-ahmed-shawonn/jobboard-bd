"""
jobs/views.py

- JobPostViewSet: employers manage their own posts (create/update/delete restricted
  to the owning employer via IsEmployer + object-level check).
- Public list/retrieve is open to any authenticated user (seekers browsing).
  Search/filter is done manually here rather than pulling in django-filter,
  since the query surface is small (title, location, active-only).
"""

from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied

from accounts.permissions import IsEmployer

from .models import JobPost
from .serializers import JobPostListSerializer, JobPostSerializer


class JobPostViewSet(viewsets.ModelViewSet):
    """
    /api/jobs/                 GET (list, filtered/searchable), POST (employer only)
    /api/jobs/{id}/            GET, PUT/PATCH, DELETE (owning employer only for writes)
    /api/jobs/?mine=true        GET — employer's own posts (active + inactive)
    /api/jobs/?search=&location=  GET — public browse filters
    """

    queryset = JobPost.objects.select_related("employer", "employer__company_profile")

    def get_serializer_class(self):
        return JobPostListSerializer if self.action == "list" else JobPostSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsEmployer()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        qs = super().get_queryset()

        mine = self.request.query_params.get("mine")
        if mine == "true" and self.request.user.is_authenticated:
            return qs.filter(employer=self.request.user)

        qs = qs.filter(is_active=True)

        search = self.request.query_params.get("search")
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(description__icontains=search))

        location = self.request.query_params.get("location")
        if location:
            qs = qs.filter(location__icontains=location)

        return qs

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.employer_id != self.request.user.id:
            raise PermissionDenied("You can only edit your own job posts.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.employer_id != self.request.user.id:
            raise PermissionDenied("You can only delete your own job posts.")
        instance.delete()
