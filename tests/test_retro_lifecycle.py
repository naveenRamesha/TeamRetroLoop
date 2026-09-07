import pytest
import json
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone

from retros.models import Retro
from teams.models import Membership, Team


@pytest.mark.django_db
def test_retro_requires_a_team_member_as_facilitator_and_only_allows_next_stage():
    users = get_user_model()
    facilitator = users.objects.create_user(username="facilitator")
    outsider = users.objects.create_user(username="outsider")
    team = Team.objects.create(name="Platform")
    Membership.objects.create(team=team, user=facilitator, role=Membership.Role.MANAGER)
    retro = Retro(team=team, sprint="Sprint 1", scheduled_at=timezone.now(), facilitator=facilitator)
    retro.full_clean()
    retro.save()

    retro.advance_to(Retro.Stage.COLLECTING)
    assert retro.stage == Retro.Stage.COLLECTING
    with pytest.raises(ValidationError):
        retro.advance_to(Retro.Stage.VOTING)

    invalid_retro = Retro(team=team, sprint="Sprint 2", scheduled_at=timezone.now(), facilitator=outsider)
    with pytest.raises(ValidationError):
        invalid_retro.full_clean()


@pytest.mark.django_db
def test_member_can_create_a_retro_but_only_facilitator_can_advance(client):
    users = get_user_model()
    facilitator = users.objects.create_user(username="facilitator")
    member = users.objects.create_user(username="member")
    team = Team.objects.create(name="Platform")
    Membership.objects.create(team=team, user=facilitator, role=Membership.Role.MANAGER)
    Membership.objects.create(team=team, user=member, role=Membership.Role.MEMBER)
    client.force_login(member)
    response = client.post("/api/retros/", data=json.dumps({"team_id": team.pk, "facilitator_id": facilitator.pk, "sprint": "Sprint 1", "scheduled_at": "2026-09-08T10:00:00Z"}), content_type="application/json")
    assert response.status_code == 201
    retro_id = response.json()["retro"]["id"]
    assert client.post(f"/api/retros/{retro_id}/advance/", data=json.dumps({"stage": "collecting"}), content_type="application/json").status_code == 403
    client.force_login(facilitator)
    assert client.post(f"/api/retros/{retro_id}/advance/", data=json.dumps({"stage": "collecting"}), content_type="application/json").status_code == 200


@pytest.mark.django_db
def test_dashboard_and_lobby_are_team_scoped(client):
    users = get_user_model()
    member = users.objects.create_user(username="member")
    outsider = users.objects.create_user(username="outsider")
    team = Team.objects.create(name="Platform")
    Membership.objects.create(team=team, user=member, role=Membership.Role.MEMBER)
    retro = Retro.objects.create(team=team, sprint="Sprint 1", scheduled_at=timezone.now(), facilitator=member)
    client.force_login(member)
    assert client.get("/api/retros/dashboard/").status_code == 200
    assert len(client.get(f"/api/retros/{retro.pk}/lobby/").json()["participants"]) == 1
    client.force_login(outsider)
    assert client.get(f"/api/retros/{retro.pk}/lobby/").status_code == 404
