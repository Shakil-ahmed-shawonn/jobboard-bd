"""
applications/views.py

MVP note: resume parsing + Claude scoring run synchronously inside the create
request. This is acceptable for a portfolio-scale app but is the first thing
to move to a background task (Celery/RQ) if applicant volume grows — the
request currently blocks on a network call to Anthropic.
"""

import logging

from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from accounts.permissions import IsSeeker

from .models import Application
from .serializers import ApplicationCreateSerializer, ApplicationSerializer
from .services import ResumeParsingError, extract_resume_text, score_resume_fit

logger = logging.getLogger(__name__)


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    /api/applications/                 POST (seeker only) — apply to a job
    /api/applications/                 GET — seeker sees own; employer sees
                                        applicants to their own job posts
    /api/applications/{id}/            GET, PATCH (employer: status update only)
    """

    http_method_names = ["get", "post", "patch", "head", "options"]

    def get_serializer_class(self):
        return ApplicationCreateSerializer if self.action == "create" else ApplicationSerializer

    def get_permissions(self):
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsSeeker()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        base = Application.objects.select_related("job", "seeker")
        if user.is_seeker():
            return base.filter(seeker=user)
        if user.is_employer():
            return base.filter(job__employer=user)
        return base.none()

    def perform_create(self, serializer):
        job = serializer.validated_data["job"]
        resume_file = serializer.validated_data["resume_file"]

        try:
            resume_text = extract_resume_text(resume_file)
        except ResumeParsingError as exc:
            # Save the application anyway (status stays 'pending', no AI score)
            # rather than blocking the seeker's application on a parsing failure.
            logger.warning("Resume parsing failed for job %s: %s", job.id, exc)
            serializer.save(seeker=self.request.user)
            return

        try:
            result = score_resume_fit(job.requirements, resume_text)
        except Exception:
            logger.exception("AI fit scoring failed for job %s", job.id)
            serializer.save(seeker=self.request.user)
            return

        serializer.save(
            seeker=self.request.user,
            ai_fit_score=result["fit_score"],
            ai_summary=result["summary"],
            ai_matched_skills=result["matched_skills"],
            ai_missing_skills=result["missing_skills"],
        )

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_employer() or instance.job.employer_id != request.user.id:
            raise PermissionDenied("Only the owning employer can update application status.")

        allowed_fields = {"status"}
        if set(request.data.keys()) - allowed_fields:
            raise ValidationError("Employers may only update the 'status' field here.")

        instance.status = request.data.get("status", instance.status)
        instance.save(update_fields=["status"])
        return Response(ApplicationSerializer(instance).data, status=status.HTTP_200_OK)
