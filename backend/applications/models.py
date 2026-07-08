"""
applications/models.py

Application links a seeker to a JobPost. The `ai_fit_score`, `ai_summary`,
`matched_skills`, and `missing_skills` fields are populated once by the
Claude API call (built in the next step) and cached here — we never
re-call the API just to render the employer's applicant list.
"""

from django.conf import settings
from django.db import models

from jobs.models import JobPost


class Application(models.Model):
    """A seeker's application to a specific JobPost, with cached AI fit results."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWED = "reviewed", "Reviewed"
        SHORTLISTED = "shortlisted", "Shortlisted"
        REJECTED = "rejected", "Rejected"

    job = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name="applications")
    seeker = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    resume_file = models.FileField(upload_to="resumes/%Y/%m/")
    cover_note = models.TextField(blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)

    # --- AI fit-scoring fields (populated after resume parsing + Claude call) ---
    ai_fit_score = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="0-100 fit score returned by Claude."
    )
    ai_summary = models.TextField(blank=True)
    ai_matched_skills = models.JSONField(default=list, blank=True)
    ai_missing_skills = models.JSONField(default=list, blank=True)

    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-ai_fit_score", "-applied_at"]
        unique_together = ("job", "seeker")  # one application per seeker per job
        indexes = [models.Index(fields=["job", "-ai_fit_score"])]

    def __str__(self) -> str:
        return f"{self.seeker} -> {self.job} ({self.status})"
