from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from teams.models import Membership, Team


class Retro(models.Model):
    class Stage(models.TextChoices):
        LOBBY = "lobby", "Lobby"
        COLLECTING = "collecting", "Collecting feedback"
        CLUSTERING = "clustering", "Clustering"
        VOTING = "voting", "Voting"
        DISCUSSION = "discussion", "Discussion"
        SUMMARY = "summary", "Summary"
        CLOSED = "closed", "Closed"

    NEXT_STAGE = {
        Stage.LOBBY: Stage.COLLECTING,
        Stage.COLLECTING: Stage.CLUSTERING,
        Stage.CLUSTERING: Stage.VOTING,
        Stage.VOTING: Stage.DISCUSSION,
        Stage.DISCUSSION: Stage.SUMMARY,
        Stage.SUMMARY: Stage.CLOSED,
    }

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="retros")
    sprint = models.CharField(max_length=100)
    scheduled_at = models.DateTimeField()
    facilitator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="facilitated_retros")
    stage = models.CharField(max_length=20, choices=Stage.choices, default=Stage.LOBBY)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.facilitator_id and self.team_id and not Membership.objects.filter(team_id=self.team_id, user_id=self.facilitator_id).exists():
            raise ValidationError({"facilitator": "The facilitator must belong to the selected team."})

    def advance_to(self, target_stage: str) -> None:
        if self.NEXT_STAGE.get(self.stage) != target_stage:
            raise ValidationError({"stage": "Only the next lifecycle stage can be selected."})
        self.stage = target_stage

