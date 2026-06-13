from django.db import migrations, models


def migrate_scraping_to_football_data(apps, schema_editor):
    Tournament = apps.get_model("tournaments", "Tournament")
    for tournament in Tournament.objects.filter(live_score_provider="scraping"):
        config = dict(tournament.live_score_config or {})
        config.pop("scores_url", None)
        if not config.get("competition_code"):
            config["competition_code"] = "WC"
        tournament.live_score_config = config
        tournament.live_score_provider = "football_data"
        tournament.save(update_fields=["live_score_provider", "live_score_config"])


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0012_scraping_live_scores"),
    ]

    operations = [
        migrations.RunPython(migrate_scraping_to_football_data, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="tournament",
            name="live_score_provider",
            field=models.CharField(
                choices=[
                    ("manual", "Manual (admin only)"),
                    ("football_data", "football-data.org"),
                ],
                default="manual",
                help_text="External feed used to update live scores for this tournament.",
                max_length=20,
            ),
        ),
    ]
