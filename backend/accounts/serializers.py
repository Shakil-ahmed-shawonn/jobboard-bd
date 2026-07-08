"""
accounts/serializers.py

Handles user registration for both roles. A single serializer covers
both because the only difference at signup time is the `role` field
and whether `company_name` is required.
"""

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import CompanyProfile, User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Validates and creates a new User.

    If role == 'employer', `company_name` is required and a
    CompanyProfile is created alongside the User.
    """

    password = serializers.CharField(write_only=True, validators=[validate_password])
    company_name = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password", "role", "company_name"]

    def validate(self, attrs):
        if attrs.get("role") == User.Role.EMPLOYER and not attrs.get("company_name"):
            raise serializers.ValidationError(
                {"company_name": "Required for employer accounts."}
            )
        return attrs

    def create(self, validated_data):
        company_name = validated_data.pop("company_name", None)
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        if user.role == User.Role.EMPLOYER:
            CompanyProfile.objects.create(user=user, company_name=company_name)

        return user


class MeSerializer(serializers.ModelSerializer):
    """Read-only serializer for GET /api/accounts/me/ — used by the frontend to
    determine the logged-in user's role after a plain username/password login."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "role"]
