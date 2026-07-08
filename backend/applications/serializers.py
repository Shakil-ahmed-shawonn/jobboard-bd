"""
applications/serializers.py

- ApplicationCreateSerializer: seeker-facing, only accepts job + resume + cover note.
  AI fields are never writable by the client.
- ApplicationSerializer: full read serializer, includes AI results and job/seeker
  summaries for the employer's applicant list.
"""

from rest_framework import serializers

from .models import Application


class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ["id", "job", "resume_file", "cover_note"]
        read_only_fields = ["id"]

    def validate_resume_file(self, value):
        if not value.name.lower().endswith((".pdf", ".docx")):
            raise serializers.ValidationError("Only .pdf or .docx files are accepted.")
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Resume must be under 5MB.")
        return value


class ApplicationSerializer(serializers.ModelSerializer):
    seeker_username = serializers.CharField(source="seeker.username", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)

    class Meta:
        model = Application
        fields = [
            "id", "job", "job_title", "seeker_username", "resume_file", "cover_note",
            "status", "ai_fit_score", "ai_summary", "ai_matched_skills",
            "ai_missing_skills", "applied_at",
        ]
        read_only_fields = fields
