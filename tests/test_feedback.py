import json
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from feedback.models import FeedbackCard
from retros.models import Retro
from teams.models import Membership, Team

@pytest.mark.django_db
def test_feedback_is_private_before_reveal_and_anonymous_after_reveal(client):
    users = get_user_model()
    author = users.objects.create_user(username="author")
    peer = users.objects.create_user(username="peer")
    team = Team.objects.create(name="Platform")
    Membership.objects.create(team=team, user=author, role=Membership.Role.MANAGER)
    Membership.objects.create(team=team, user=peer, role=Membership.Role.MEMBER)
    retro = Retro.objects.create(team=team, sprint="Sprint 1", scheduled_at=timezone.now(), facilitator=author, stage=Retro.Stage.COLLECTING)
    client.force_login(author)
    created = client.post(f"/api/retros/{retro.pk}/feedback/", data=json.dumps({"category": "start", "text": "Pair more", "anonymous": True}), content_type="application/json")
    assert created.status_code == 201
    card_id = created.json()["card"]["id"]
    client.force_login(peer)
    assert client.get(f"/api/retros/{retro.pk}/feedback/").json()["cards"] == []
    retro.stage = Retro.Stage.CLUSTERING
    retro.save(update_fields=["stage"])
    revealed = client.get(f"/api/retros/{retro.pk}/feedback/").json()["cards"]
    assert revealed[0]["author"] is None
    client.force_login(author)
    assert client.patch(f"/api/retros/{retro.pk}/feedback/{card_id}/", data=json.dumps({"text": "Pair more often"}), content_type="application/json").status_code == 400
