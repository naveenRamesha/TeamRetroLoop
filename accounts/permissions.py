"""Shared API authorization helpers."""

from collections.abc import Callable
from functools import wraps
from typing import Any

from django.http import HttpRequest, HttpResponse, JsonResponse


def api_login_required(
    view: Callable[..., HttpResponse],
) -> Callable[..., HttpResponse]:
    """Return JSON instead of redirecting unauthenticated API clients."""

    @wraps(view)
    def wrapped(request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if not request.user.is_authenticated:
            return JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)
        return view(request, *args, **kwargs)

    return wrapped

