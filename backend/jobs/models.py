"""
jobs/models.py

JobPost is owned by an employer User. Views/serializers for this app
are built in the next step (job posting + browse/search).
"""

from django.conf import settings
from django.db import models


class JobPost(models.Model):
    """A job listing created by an employer."""

    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="job_posts"
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    requirements = models.TextField(help_text="Plain-text requirements; sent to Claude for fit scoring.")
    location = models.CharField(max_length=120, blank=True)
    salary_range = models.CharField(max_length=80, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["is_active", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.title} @ {self.employer}"
