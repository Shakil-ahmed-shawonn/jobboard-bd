"""jobs/urls.py — router for JobPostViewSet."""

from rest_framework.routers import DefaultRouter

from .views import JobPostViewSet

router = DefaultRouter()
router.register(r"", JobPostViewSet, basename="jobpost")

urlpatterns = router.urls
