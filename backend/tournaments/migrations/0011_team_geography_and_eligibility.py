from django.db import migrations, models


def backfill_team_geography(apps, schema_editor):
    Team = apps.get_model("tournaments", "Team")
    from tournaments.services.team_geography import geography_for_team_code

    for team in Team.objects.all():
        geo = geography_for_team_code(team.code, "")
        team.team_type = geo["team_type"]
        if not team.country_code:
            team.country_code = geo["country_code"]
        if not team.continent:
            team.continent = geo["continent"]
        team.save(
            update_fields=["team_type", "country_code", "continent"]
        )


def backfill_tournament_eligibility(apps, schema_editor):
    Tournament = apps.get_model("tournaments", "Tournament")
    from tournaments.services.team_eligibility import default_team_eligibility_for_competition

    for tournament in Tournament.objects.all():
        defaults = default_team_eligibility_for_competition(tournament.competition_type)
        for key, value in defaults.items():
            setattr(tournament, key, value)
        tournament.save(update_fields=list(defaults.keys()))


def sync_world_cup_eligibility(apps, schema_editor):
    """Apply full WC defaults (standing rules + team eligibility) after new columns exist."""
    Tournament = apps.get_model("tournaments", "Tournament")
    StandingRuleSet = apps.get_model("tournaments", "StandingRuleSet")

    ruleset = StandingRuleSet.objects.filter(slug="fifa-world-cup-48-teams").first()
    if not ruleset:
        return

    live_config = {"league_id": 1, "season": 2026}
    for tournament in Tournament.objects.filter(name="FIFA World Cup", year=2026):
        tournament.competition_type = "world_cup"
        tournament.allowed_team_type = "national"
        tournament.team_scope = "worldwide"
        tournament.allowed_continent = ""
        tournament.allowed_country_code = ""
        tournament.allowed_division = ""
        tournament.standing_rule_set_id = ruleset.id
        tournament.standing_rules = ruleset.engine
        tournament.qualifiers_per_group = ruleset.qualifiers_per_group
        tournament.live_score_provider = "api_football"
        tournament.live_score_config = live_config
        tournament.save(
            update_fields=[
                "competition_type",
                "allowed_team_type",
                "team_scope",
                "allowed_continent",
                "allowed_country_code",
                "allowed_division",
                "standing_rule_set_id",
                "standing_rules",
                "qualifiers_per_group",
                "live_score_provider",
                "live_score_config",
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0010_tournament_competition_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="team_type",
            field=models.CharField(
                choices=[("national", "National team (country)"), ("club", "Club")],
                default="national",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="team",
            name="country_code",
            field=models.CharField(
                blank=True,
                default="",
                help_text="ISO country code (e.g. eg, mx, gb-eng). Nation for national teams; home country for clubs.",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="team",
            name="continent",
            field=models.CharField(
                blank=True,
                choices=[
                    ("africa", "Africa"),
                    ("asia", "Asia"),
                    ("europe", "Europe"),
                    ("north_america", "North America"),
                    ("south_america", "South America"),
                    ("oceania", "Oceania"),
                ],
                default="",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="team",
            name="division",
            field=models.CharField(
                blank=True,
                default="",
                help_text="League or division (clubs only), e.g. Premier League.",
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name="tournament",
            name="allowed_team_type",
            field=models.CharField(
                choices=[
                    ("national", "National teams only"),
                    ("club", "Clubs only"),
                    ("any", "National or club"),
                ],
                default="national",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="tournament",
            name="team_scope",
            field=models.CharField(
                choices=[
                    ("worldwide", "Worldwide"),
                    ("continent", "One continent"),
                    ("country", "One country"),
                    ("division", "One division (clubs)"),
                ],
                default="worldwide",
                max_length=16,
            ),
        ),
        migrations.AddField(
            model_name="tournament",
            name="allowed_continent",
            field=models.CharField(
                blank=True,
                choices=[
                    ("africa", "Africa"),
                    ("asia", "Asia"),
                    ("europe", "Europe"),
                    ("north_america", "North America"),
                    ("south_america", "South America"),
                    ("oceania", "Oceania"),
                ],
                default="",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="tournament",
            name="allowed_country_code",
            field=models.CharField(blank=True, default="", max_length=16),
        ),
        migrations.AddField(
            model_name="tournament",
            name="allowed_division",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddIndex(
            model_name="team",
            index=models.Index(fields=["team_type"], name="tournaments__team_ty_6e8a21_idx"),
        ),
        migrations.AddIndex(
            model_name="team",
            index=models.Index(fields=["continent"], name="tournaments__contine_2f4b90_idx"),
        ),
        migrations.AddIndex(
            model_name="team",
            index=models.Index(fields=["country_code"], name="tournaments__country_8a1c32_idx"),
        ),
        migrations.RunPython(backfill_team_geography, migrations.RunPython.noop),
        migrations.RunPython(backfill_tournament_eligibility, migrations.RunPython.noop),
        migrations.RunPython(sync_world_cup_eligibility, migrations.RunPython.noop),
    ]
