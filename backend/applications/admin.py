"""applications/admin.py — exposes Application in Django admin."""
from django.contrib import admin
from .models import Application

admin.site.register(Application)
