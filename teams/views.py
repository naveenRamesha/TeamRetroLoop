"""Team and membership API endpoints."""

import json
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods

from accounts.permissions import api_login_required
from teams.models import Membership, Team


def _json_body(request: HttpRequest) -> dict[str, Any] | None:
    try:
        value = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
    return value if isinstance(value, dict) else None


def _user_data(user: Any) -> dict[str, Any]:
    return {"id": user.pk, "username": user.get_username()}


def _membership_data(membership: Membership) -> dict[str, Any]:
    return {"user": _user_data(membership.user), "role": membership.role}


def _team_data(team: Team) -> dict[str, Any]:
    return {"id": team.pk, "name": team.name, "created_at": team.created_at.isoformat()}


def _membership_for_request(team_id: int, user: Any) -> Membership:
    return get_object_or_404(
        Membership.objects.select_related("team", "user"), team_id=team_id, user=user
    )


def _manager_membership(team_id: int, user: Any) -> Membership | None:
    membership = _membership_for_request(team_id, user)
    if membership.role != Membership.Role.MANAGER:
        return None
    return membership


def _has_other_manager(team_id: int, membership_id: int) -> bool:
    return Membership.objects.filter(team_id=team_id, role=Membership.Role.MANAGER).exclude(
        pk=membership_id
    ).exists()


@require_http_methods(["GET", "POST"])
@api_login_required
def team_collection(request: HttpRequest) -> JsonResponse:
    if request.method == "GET":
        memberships = Membership.objects.filter(user=request.user).select_related("team")
        return JsonResponse(
            {
                "teams": [
                    {**_team_data(membership.team), "role": membership.role}
                    for membership in memberships
                ]
            }
        )

    payload = _json_body(request)
    name = payload.get("name") if payload else None
    if not isinstance(name, str) or not name.strip():
        return JsonResponse({"detail": "name is required."}, status=400)
    if len(name.strip()) > 100:
        return JsonResponse({"detail": "name must be 100 characters or fewer."}, status=400)

    with transaction.atomic():
        team = Team.objects.create(name=name.strip())
        membership = Membership.objects.create(
            team=team, user=request.user, role=Membership.Role.MANAGER
        )
    return JsonResponse({"team": {**_team_data(team), "role": membership.role}}, status=201)


@require_http_methods(["GET"])
@api_login_required
def team_detail(request: HttpRequest, team_id: int) -> JsonResponse:
    membership = _membership_for_request(team_id, request.user)
    members = membership.team.memberships.select_related("user")
    return JsonResponse(
        {
            "team": {
                **_team_data(membership.team),
                "role": membership.role,
                "members": [_membership_data(member) for member in members],
            }
        }
    )


@require_http_methods(["POST"])
@api_login_required
def membership_collection(request: HttpRequest, team_id: int) -> JsonResponse:
    manager = _manager_membership(team_id, request.user)
    if manager is None:
        return JsonResponse({"detail": "Only team managers can manage members."}, status=403)

    payload = _json_body(request)
    username = payload.get("username") if payload else None
    role = payload.get("role", Membership.Role.MEMBER) if payload else Membership.Role.MEMBER
    if not isinstance(username, str) or not username:
        return JsonResponse({"detail": "username is required."}, status=400)
    if role not in Membership.Role.values:
        return JsonResponse({"detail": "role must be manager or member."}, status=400)

    user = get_object_or_404(get_user_model(), username=username)
    membership, created = Membership.objects.get_or_create(
        team=manager.team, user=user, defaults={"role": role}
    )
    if not created:
        return JsonResponse({"detail": "User is already a team member."}, status=400)
    return JsonResponse({"membership": _membership_data(membership)}, status=201)


@require_http_methods(["PATCH", "DELETE"])
@api_login_required
def membership_detail(request: HttpRequest, team_id: int, user_id: int) -> JsonResponse:
    manager = _manager_membership(team_id, request.user)
    if manager is None:
        return JsonResponse({"detail": "Only team managers can manage members."}, status=403)
    membership = get_object_or_404(
        Membership.objects.select_related("user"), team=manager.team, user_id=user_id
    )

    if request.method == "DELETE":
        if membership.role == Membership.Role.MANAGER and not _has_other_manager(team_id, membership.pk):
            return JsonResponse({"detail": "A team must have at least one manager."}, status=400)
        membership.delete()
        return JsonResponse({}, status=204)

    payload = _json_body(request)
    role = payload.get("role") if payload else None
    if role not in Membership.Role.values:
        return JsonResponse({"detail": "role must be manager or member."}, status=400)
    if (
        membership.role == Membership.Role.MANAGER
        and role != Membership.Role.MANAGER
        and not _has_other_manager(team_id, membership.pk)
    ):
        return JsonResponse({"detail": "A team must have at least one manager."}, status=400)

    membership.role = role
    membership.save(update_fields=["role"])
    return JsonResponse({"membership": _membership_data(membership)})

