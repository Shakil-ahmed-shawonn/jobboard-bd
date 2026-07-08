"""
jobs/serializers.py

Two serializers:
- JobPostSerializer: full read/write, used for create/update by the owning employer.
- JobPostListSerializer: lighter fields for the public browse list (perf: avoids
  sending full `requirements`/`description` text in list views).
"""

from rest_framework import serializers

from .models import JobPost


class JobPostSerializer(serializers.ModelSerializer):
    employer_username = serializers.CharField(source="employer.username", read_only=True)
    company_name = serializers.CharField(
        source="employer.company_profile.company_name", read_only=True, default=""
    )

    class Meta:
        model = JobPost
        fields = [
            "id", "title", "description", "requirements", "location",
            "salary_range", "is_active", "created_at", "updated_at",
            "employer_username", "company_name",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "employer_username", "company_name"]


class JobPostListSerializer(serializers.ModelSerializer):
    """Slim serializer for the public job browse/search list."""

    company_name = serializers.CharField(
        source="employer.company_profile.company_name", read_only=True, default=""
    )

    class Meta:
        model = JobPost
        fields = ["id", "title", "location", "salary_range", "company_name", "created_at"]
