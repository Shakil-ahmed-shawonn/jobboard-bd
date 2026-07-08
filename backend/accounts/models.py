"""
accounts/models.py

Defines the custom User model (role-based: employer or seeker) and the
CompanyProfile model owned by employer users.

Why a custom User instead of Django's default:
- We need a `role` field baked in from day one. Swapping AUTH_USER_MODEL
  after migrations exist is painful, so we start correctly.
Docs: https://docs.djangoproject.com/en/5.0/topics/auth/customizing/
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user with a role flag.

    Attributes:
        role: 'employer' or 'seeker'. Drives permission checks and
              which dashboard/serializers apply to this account.
    """

    class Role(models.TextChoices):
        EMPLOYER = "employer", "Employer"
        SEEKER = "seeker", "Job Seeker"

    role = models.CharField(max_length=10, choices=Role.choices)

    def is_employer(self) -> bool:
        return self.role == self.Role.EMPLOYER

    def is_seeker(self) -> bool:
        return self.role == self.Role.SEEKER

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"


class CompanyProfile(models.Model):
    """
    One-to-one profile attached to an employer User.
    Holds public-facing company info shown on job listings.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="company_profile"
    )
    company_name = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="company_logos/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.company_name
