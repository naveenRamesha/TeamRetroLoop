from django.conf import settings
from django.db import models
from retros.models import Retro
from topics.models import Topic

class FeedbackCard(models.Model):
    class Category(models.TextChoices):
        START = "start", "Start"
        STOP = "stop", "Stop"
        CONTINUE = "continue", "Continue"
    retro = models.ForeignKey(Retro, on_delete=models.CASCADE, related_name="feedback_cards")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="feedback_cards")
    category = models.CharField(max_length=10, choices=Category.choices)
    text = models.TextField()
    anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topic = models.ForeignKey(Topic, null=True, blank=True, on_delete=models.SET_NULL, related_name="cards")
