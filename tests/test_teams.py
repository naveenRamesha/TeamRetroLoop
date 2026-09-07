import json

import pytest
from django.contrib.auth import get_user_model

from teams.models import Membership, Team


def json_request(client, method, path, payload=None):
    return getattr(client, method)(
        path,
        data=json.dumps(payload) if payload is not None else None,
        content_type="application/json",
    )


@pytest.fixture
def users(db):
    user_model = get_user_model()
    return {
        "manager": user_model.objects.create_user(username="manager", password="password"),
        "member": user_model.objects.create_user(username="member", password="password"),
        "outsider": user_model.objects.create_user(username="outsider", password="password"),
    }


@pytest.mark.django_db
def test_authenticated_user_can_create_a_team_and_becomes_its_manager(client, users):
    client.force_login(users["manager"])

    response = json_request(client, "post", "/api/teams/", {"name": "Platform"})

    assert response.status_code == 201
    team = Team.objects.get(name="Platform")
    assert response.json()["team"]["id"] == team.pk
    assert Membership.objects.get(team=team, user=users["manager"]).role == Membership.Role.MANAGER


@pytest.mark.django_db
def test_user_can_list_only_their_own_teams(client, users):
    manager_team = Team.objects.create(name="Manager team")
    other_team = Team.objects.create(name="Other team")
    Membership.objects.create(team=manager_team, user=users["manager"], role=Membership.Role.MANAGER)
    Membership.objects.create(team=other_team, user=users["outsider"], role=Membership.Role.MANAGER)
    client.force_login(users["manager"])

    response = client.get("/api/teams/")

    assert response.status_code == 200
    assert response.json()["teams"] == [
        {**response.json()["teams"][0], "id": manager_team.pk, "name": "Manager team", "role": "manager"}
    ]


@pytest.mark.django_db
def test_team_members_can_view_members_but_outsiders_cannot(client, users):
    team = Team.objects.create(name="Platform")
    Membership.objects.create(team=team, user=users["manager"], role=Membership.Role.MANAGER)
    Membership.objects.create(team=team, user=users["member"], role=Membership.Role.MEMBER)
    client.force_login(users["member"])

    member_response = client.get(f"/api/teams/{team.pk}/")

    assert member_response.status_code == 200
    assert {member["user"]["username"] for member in member_response.json()["team"]["members"]} == {
        "manager",
        "member",
    }

    client.force_login(users["outsider"])
    outsider_response = client.get(f"/api/teams/{team.pk}/")
    assert outsider_response.status_code == 404


@pytest.mark.django_db
def test_manager_can_add_and_promote_a_member(client, users):
    team = Team.objects.create(name="Platform")
    Membership.objects.create(team=team, user=users["manager"], role=Membership.Role.MANAGER)
    client.force_login(users["manager"])

    add_response = json_request(
        client, "post", f"/api/teams/{team.pk}/members/", {"username": "member"}
    )
    promote_response = json_request(
        client,
        "patch",
        f"/api/teams/{team.pk}/members/{users['member'].pk}/",
        {"role": "manager"},
    )

    assert add_response.status_code == 201
    assert add_response.json()["membership"]["role"] == "member"
    assert promote_response.status_code == 200
    assert Membership.objects.get(team=team, user=users["member"]).role == Membership.Role.MANAGER


@pytest.mark.django_db
def test_non_manager_cannot_change_the_team_roster(client, users):
    team = Team.objects.create(name="Platform")
    Membership.objects.create(team=team, user=users["manager"], role=Membership.Role.MANAGER)
    Membership.objects.create(team=team, user=users["member"], role=Membership.Role.MEMBER)
    client.force_login(users["member"])

    response = json_request(
        client, "post", f"/api/teams/{team.pk}/members/", {"username": "outsider"}
    )

    assert response.status_code == 403
    assert not Membership.objects.filter(team=team, user=users["outsider"]).exists()


@pytest.mark.django_db
def test_manager_can_remove_a_member_but_not_the_last_manager(client, users):
    team = Team.objects.create(name="Platform")
    Membership.objects.create(team=team, user=users["manager"], role=Membership.Role.MANAGER)
    Membership.objects.create(team=team, user=users["member"], role=Membership.Role.MEMBER)
    client.force_login(users["manager"])

    remove_response = client.delete(f"/api/teams/{team.pk}/members/{users['member'].pk}/")
    remove_manager_response = client.delete(
        f"/api/teams/{team.pk}/members/{users['manager'].pk}/"
    )

    assert remove_response.status_code == 204
    assert not Membership.objects.filter(team=team, user=users["member"]).exists()
    assert remove_manager_response.status_code == 400
    assert Membership.objects.filter(team=team, user=users["manager"]).exists()
