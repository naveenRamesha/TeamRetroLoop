import json
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from accounts.permissions import api_login_required
from retros.models import Retro
from teams.models import Membership


def _body(request: HttpRequest) -> dict[str, Any] | None:
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _data(retro: Retro) -> dict[str, Any]:
    return {"id": retro.pk, "team_id": retro.team_id, "sprint": retro.sprint, "scheduled_at": retro.scheduled_at.isoformat(), "facilitator_id": retro.facilitator_id, "stage": retro.stage}


@require_http_methods(["GET"])
@api_login_required
def dashboard(request: HttpRequest) -> JsonResponse:
    retros = Retro.objects.filter(team__memberships__user=request.user).distinct().order_by("scheduled_at")
    now = timezone.now()
    return JsonResponse({"upcoming": [_data(retro) for retro in retros if retro.scheduled_at >= now], "recent": [_data(retro) for retro in retros if retro.scheduled_at < now]})


@require_http_methods(["GET"])
@api_login_required
def lobby(request: HttpRequest, retro_id: int) -> JsonResponse:
    retro = get_object_or_404(Retro, pk=retro_id, team__memberships__user=request.user)
    memberships = retro.team.memberships.select_related("user")
    return JsonResponse({"retro": _data(retro), "team": {"id": retro.team_id, "name": retro.team.name}, "participants": [{"id": m.user_id, "username": m.user.username, "role": m.role} for m in memberships]})


@require_http_methods(["GET", "POST"])
@api_login_required
def retro_collection(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        retros = Retro.objects.filter(team__memberships__user=request.user).distinct().order_by("scheduled_at")
        return JsonResponse({"retros": [_data(retro) for retro in retros]})
    payload = _body(request)
    if payload is None:
        return JsonResponse({"detail": "Request body must be a JSON object."}, status=400)
    team_id, facilitator_id = payload.get("team_id"), payload.get("facilitator_id")
    sprint, scheduled_at = payload.get("sprint"), parse_datetime(payload.get("scheduled_at", "")) if isinstance(payload.get("scheduled_at"), str) else None
    if not isinstance(team_id, int) or not isinstance(facilitator_id, int) or not isinstance(sprint, str) or not sprint.strip() or scheduled_at is None:
        return JsonResponse({"detail": "team_id, facilitator_id, sprint, and an ISO 8601 scheduled_at are required."}, status=400)
    if not Membership.objects.filter(team_id=team_id, user=request.user).exists():
        return JsonResponse({"detail": "Team not found."}, status=404)
    facilitator = get_object_or_404(get_user_model(), pk=facilitator_id)
    retro = Retro(team_id=team_id, sprint=sprint.strip(), scheduled_at=scheduled_at, facilitator=facilitator)
    try:
        retro.full_clean()
    except ValidationError as error:
        return JsonResponse({"detail": error.message_dict}, status=400)
    retro.save()
    return JsonResponse({"retro": _data(retro)}, status=201)


@require_POST
@api_login_required
def advance_retro(request: HttpRequest, retro_id: int) -> JsonResponse:
    payload = _body(request)
    stage = payload.get("stage") if payload else None
    with transaction.atomic():
        retro = get_object_or_404(Retro.objects.select_for_update(), pk=retro_id, team__memberships__user=request.user)
        if retro.facilitator_id != request.user.pk:
            return JsonResponse({"detail": "Only the facilitator can advance this retro."}, status=403)
        try:
            retro.advance_to(stage)
        except ValidationError as error:
            return JsonResponse({"detail": error.message_dict}, status=400)
        retro.save(update_fields=["stage"])
    return JsonResponse({"retro": _data(retro)})


@require_POST
@api_login_required
def reveal(request: HttpRequest, retro_id: int) -> JsonResponse:
    retro = get_object_or_404(Retro, pk=retro_id, team__memberships__user=request.user)
    if retro.facilitator_id != request.user.pk:
        return JsonResponse({"detail": "Only the facilitator can reveal feedback."}, status=403)
    if retro.stage != Retro.Stage.COLLECTING:
        return JsonResponse({"detail": "Feedback can only be revealed during collection."}, status=400)
    retro.stage = Retro.Stage.CLUSTERING
    retro.save(update_fields=["stage"])
    return JsonResponse({"retro": _data(retro)})
