"""jobs/admin.py — exposes JobPost in Django admin."""
from django.contrib import admin
from .models import JobPost

admin.site.register(JobPost)
