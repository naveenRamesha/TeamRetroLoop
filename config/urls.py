"""URL routing for TeamRetroLoop."""

from django.http import HttpResponse
from django.urls import path


def home(_: object) -> HttpResponse:
    """Return a minimal health response for the application root."""
    return HttpResponse("TeamRetroLoop is running.")


urlpatterns = [
    path("", home, name="home"),
]

