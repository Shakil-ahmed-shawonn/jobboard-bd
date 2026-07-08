"""accounts/urls.py — registration + current-user routes. Login handled by SimpleJWT in root urls.py."""

from django.urls import path

from .views import MeView, RegisterView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
]
