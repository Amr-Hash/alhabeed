import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def subscribe_existing_users_to_world_cup(apps, schema_editor):
    from tournaments.services.subscriptions import subscribe_all_users_to_default_world_cup

    subscribe_all_users_to_default_world_cup()


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0007_standing_rule_sets"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="TournamentSubscription",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tournament",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tournament_subscriptions",
                        to="tournaments.tournament",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tournament_subscriptions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["user", "-created_at"],
                        name="tournaments__user_id_91a4c2_idx",
                    ),
                    models.Index(
                        fields=["tournament", "user"],
                        name="tournaments__tournam_4b8e11_idx",
                    ),
                ],
                "unique_together": {("user", "tournament")},
            },
        ),
        migrations.RunPython(
            subscribe_existing_users_to_world_cup,
            migrations.RunPython.noop,
        ),
    ]
