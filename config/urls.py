"""URL routing for TeamRetroLoop."""

from django.http import HttpResponse
from django.urls import include, path


def home(_: object) -> HttpResponse:
    """Return a minimal health response for the application root."""
    return HttpResponse("TeamRetroLoop is running.")


urlpatterns = [
    path("", home, name="home"),
    path("api/auth/", include("accounts.urls")),
    path("api/teams/", include("teams.urls")),
    path("api/retros/", include("retros.urls")),
    path("api/retros/<int:retro_id>/feedback/", include("feedback.urls")),
]
