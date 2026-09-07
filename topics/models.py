from django.db import models
from retros.models import Retro

class Topic(models.Model):
    retro = models.ForeignKey(Retro, on_delete=models.CASCADE, related_name="topics")
    name = models.CharField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ["created_at", "pk"]
        constraints = [models.UniqueConstraint(fields=["retro", "name"], name="unique_topic_name_per_retro")]
