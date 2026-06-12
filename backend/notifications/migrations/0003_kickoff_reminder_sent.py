from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tournaments", "0011_team_geography_and_eligibility"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("notifications", "0002_pushsubscription_and_kickoff_reminder"),
    ]

    operations = [
        migrations.CreateModel(
            name="KickoffReminderSent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("sent_at", models.DateTimeField(auto_now_add=True)),
                (
                    "match",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="kickoff_reminders_sent",
                        to="tournaments.match",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="kickoff_reminders_sent",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "constraints": [
                    models.UniqueConstraint(
                        fields=("user", "match"),
                        name="notifications_kickoff_reminder_once",
                    )
                ],
            },
        ),
    ]
