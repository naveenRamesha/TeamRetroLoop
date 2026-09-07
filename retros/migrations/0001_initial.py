import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("teams", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Retro",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("sprint", models.CharField(max_length=100)),
                ("scheduled_at", models.DateTimeField()),
                ("stage", models.CharField(choices=[("lobby", "Lobby"), ("collecting", "Collecting feedback"), ("clustering", "Clustering"), ("voting", "Voting"), ("discussion", "Discussion"), ("summary", "Summary"), ("closed", "Closed")], default="lobby", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("facilitator", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="facilitated_retros", to=settings.AUTH_USER_MODEL)),
                ("team", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="retros", to="teams.team")),
            ],
        )
    ]
