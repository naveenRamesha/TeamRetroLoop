"""Session authentication and profile API endpoints."""

import json
from typing import Any

from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from accounts.permissions import api_login_required


def _profile(user: Any) -> dict[str, Any]:
    return {
        "id": user.pk,
        "username": user.get_username(),
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
    }


def _json_body(request: HttpRequest) -> dict[str, Any] | None:
    try:
        value = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return value if isinstance(value, dict) else None


@require_GET
def csrf_token(request: HttpRequest) -> JsonResponse:
    """Issue the CSRF token required by state-changing session endpoints."""
    return JsonResponse({"csrfToken": get_token(request)})


@require_POST
def login_view(request: HttpRequest) -> JsonResponse:
    """Authenticate credentials and establish a session."""
    payload = _json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Request body must be a JSON object."}, status=400)

    username = payload.get("username")
    password = payload.get("password")
    if not isinstance(username, str) or not isinstance(password, str):
        return JsonResponse({"detail": "Username and password are required."}, status=400)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"detail": "Invalid username or password."}, status=401)

    login(request, user)
    return JsonResponse({"user": _profile(user)})


@require_POST
@api_login_required
def logout_view(request: HttpRequest) -> JsonResponse:
    """End the authenticated user's current session."""
    logout(request)
    return JsonResponse({}, status=204)


@require_http_methods(["GET", "PATCH"])
@api_login_required
def profile_view(request: HttpRequest) -> JsonResponse:
    """Read or safely update the authenticated user's profile."""
    if request.method == "GET":
        return JsonResponse({"user": _profile(request.user)})

    payload = _json_body(request)
    if payload is None:
        return JsonResponse({"detail": "Request body must be a JSON object."}, status=400)

    editable_fields = {"first_name", "last_name", "email"}
    unexpected_fields = set(payload) - editable_fields
    if unexpected_fields:
        return JsonResponse({"detail": "Only first_name, last_name, and email can be updated."}, status=400)
    if not payload:
        return JsonResponse({"detail": "Provide at least one profile field to update."}, status=400)

    for field, value in payload.items():
        if not isinstance(value, str):
            return JsonResponse({"detail": f"{field} must be a string."}, status=400)
    if "email" in payload:
        try:
            validate_email(payload["email"])
        except ValidationError:
            return JsonResponse({"detail": "email must be a valid email address."}, status=400)

    for field, value in payload.items():
        setattr(request.user, field, value)
    request.user.save(update_fields=list(payload))
    return JsonResponse({"user": _profile(request.user)})
