import json

import pytest
from django.contrib.auth import get_user_model
from django.test import Client


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(
        username="alex",
        password="correct-horse-battery-staple",
        first_name="Alex",
        last_name="Smith",
        email="alex@example.com",
    )


def json_request(client, method, path, payload=None):
    return getattr(client, method)(
        path,
        data=json.dumps(payload) if payload is not None else None,
        content_type="application/json",
    )


@pytest.mark.django_db
def test_login_creates_a_session_and_returns_the_profile(client, user):
    response = json_request(
        client,
        "post",
        "/api/auth/login/",
        {"username": user.username, "password": "correct-horse-battery-staple"},
    )

    assert response.status_code == 200
    assert response.json()["user"] == {
        "id": user.pk,
        "username": "alex",
        "first_name": "Alex",
        "last_name": "Smith",
        "email": "alex@example.com",
    }
    assert "sessionid" in client.cookies


@pytest.mark.django_db
def test_login_rejects_invalid_credentials(client, user):
    response = json_request(
        client,
        "post",
        "/api/auth/login/",
        {"username": user.username, "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert "sessionid" not in client.cookies


@pytest.mark.django_db
def test_profile_requires_authentication(client):
    response = client.get("/api/auth/me/")

    assert response.status_code == 401


@pytest.mark.django_db
def test_profile_returns_only_the_authenticated_user(client, user):
    other_user = get_user_model().objects.create_user(
        username="sam",
        password="another-password",
        email="sam@example.com",
    )
    client.force_login(user)

    response = client.get("/api/auth/me/")

    assert response.status_code == 200
    assert response.json()["user"]["id"] == user.pk
    assert response.json()["user"]["id"] != other_user.pk


@pytest.mark.django_db
def test_profile_update_changes_only_the_authenticated_user(client, user):
    other_user = get_user_model().objects.create_user(
        username="sam",
        password="another-password",
        email="sam@example.com",
    )
    client.force_login(user)

    response = json_request(
        client,
        "patch",
        "/api/auth/me/",
        {"first_name": "Alexandra", "email": "alexandra@example.com"},
    )

    assert response.status_code == 200
    user.refresh_from_db()
    other_user.refresh_from_db()
    assert user.first_name == "Alexandra"
    assert user.email == "alexandra@example.com"
    assert other_user.email == "sam@example.com"


@pytest.mark.django_db
def test_logout_ends_the_current_session(client, user):
    client.force_login(user)

    response = client.post("/api/auth/logout/")

    assert response.status_code == 204
    assert client.get("/api/auth/me/").status_code == 401


@pytest.mark.django_db
def test_browser_session_requests_require_and_accept_a_csrf_token(user):
    client = Client(enforce_csrf_checks=True)

    csrf_response = client.get("/api/auth/csrf/")
    assert csrf_response.status_code == 200
    csrf_token = client.cookies["csrftoken"].value

    rejected_login = json_request(
        client,
        "post",
        "/api/auth/login/",
        {"username": user.username, "password": "correct-horse-battery-staple"},
    )
    assert rejected_login.status_code == 403

    accepted_login = client.post(
        "/api/auth/login/",
        data=json.dumps({"username": user.username, "password": "correct-horse-battery-staple"}),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=csrf_token,
    )
    assert accepted_login.status_code == 200

    rejected_logout = client.post("/api/auth/logout/")
    assert rejected_logout.status_code == 403

    accepted_logout = client.post(
        "/api/auth/logout/", HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value
    )
    assert accepted_logout.status_code == 204
