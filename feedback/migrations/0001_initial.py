import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("retros", "0001_initial"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="FeedbackCard", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("category", models.CharField(choices=[("start", "Start"), ("stop", "Stop"), ("continue", "Continue")], max_length=10)),
        ("text", models.TextField()), ("anonymous", models.BooleanField(default=False)),
        ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
        ("author", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="feedback_cards", to=settings.AUTH_USER_MODEL)),
        ("retro", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="feedback_cards", to="retros.retro")),
    ], options={"ordering": ["category", "created_at", "pk"]})]
