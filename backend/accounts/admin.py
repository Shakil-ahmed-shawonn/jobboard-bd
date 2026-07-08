"""accounts/admin.py — exposes User and CompanyProfile in Django admin for ops/debugging."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CompanyProfile, User


class CustomUserAdmin(UserAdmin):
    """Extends default UserAdmin to surface the `role` field in list view and edit form."""

    list_display = ("username", "email", "role", "is_staff")
    fieldsets = UserAdmin.fieldsets + (("Role", {"fields": ("role",)}),)


admin.site.register(User, CustomUserAdmin)
admin.site.register(CompanyProfile)
