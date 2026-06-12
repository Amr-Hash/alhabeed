from django.db import migrations, models
import django.db.models.deletion


def seed_standing_rule_sets(apps, schema_editor):
    StandingRuleSet = apps.get_model("tournaments", "StandingRuleSet")
    Tournament = apps.get_model("tournaments", "Tournament")

    from tournaments.services.standing_rule_sets import default_rule_sets

    slug_by_engine = {}
    for row in default_rule_sets():
        ruleset, _created = StandingRuleSet.objects.update_or_create(
            slug=row["slug"],
            defaults={**row, "is_active": True},
        )
        slug_by_engine[row["engine"]] = ruleset

    engine_map = {
        "fifa_world_cup": slug_by_engine.get("fifa-world-cup-2026"),
        "uefa_champions_league": slug_by_engine.get("uefa-champions-league-standard"),
        "simple": slug_by_engine.get("simple-default"),
    }
    for tournament in Tournament.objects.all():
        ruleset = engine_map.get(tournament.standing_rules)
        if ruleset and not tournament.standing_rule_set_id:
            tournament.standing_rule_set_id = ruleset.id
            tournament.save(update_fields=["standing_rule_set_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0006_live_scores"),
    ]

    operations = [
        migrations.CreateModel(
            name="StandingRuleSet",
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
                ("slug", models.SlugField(max_length=64, unique=True)),
                ("name", models.CharField(max_length=200)),
                ("name_ar", models.CharField(blank=True, default="", max_length=200)),
                (
                    "competition_type",
                    models.CharField(
                        choices=[
                            ("world_cup", "FIFA World Cup"),
                            ("champions_league", "UEFA Champions League"),
                            ("other", "Other"),
                        ],
                        default="other",
                        max_length=32,
                    ),
                ),
                (
                    "version",
                    models.CharField(
                        help_text="Rule-set version label, e.g. 2026 or 2024-25.",
                        max_length=32,
                    ),
                ),
                (
                    "engine",
                    models.CharField(
                        choices=[
                            ("fifa_world_cup", "FIFA World Cup tie-breakers"),
                            ("uefa_champions_league", "UEFA Champions League tie-breakers"),
                            ("simple", "Simple (points → GD → GF)"),
                        ],
                        max_length=32,
                    ),
                ),
                ("qualifiers_per_group", models.PositiveSmallIntegerField(default=2)),
                (
                    "best_third_place_qualifiers",
                    models.PositiveSmallIntegerField(
                        default=0,
                        help_text="Best third-placed teams that advance (FIFA World Cup style).",
                    ),
                ),
                ("tiebreakers_en", models.JSONField(blank=True, default=list)),
                ("tiebreakers_ar", models.JSONField(blank=True, default=list)),
                ("third_place_tiebreakers_en", models.JSONField(blank=True, default=list)),
                ("third_place_tiebreakers_ar", models.JSONField(blank=True, default=list)),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Only active rule sets can be assigned to new tournaments.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["competition_type", "-version", "name"],
            },
        ),
        migrations.AddIndex(
            model_name="standingruleset",
            index=models.Index(
                fields=["competition_type", "is_active"],
                name="tournaments__competi_6e2f0a_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="standingruleset",
            index=models.Index(fields=["engine"], name="tournaments__engine_2c8b91_idx"),
        ),
        migrations.AddField(
            model_name="tournament",
            name="standing_rule_set",
            field=models.ForeignKey(
                blank=True,
                help_text="Versioned standing/qualification rules for this tournament.",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="tournaments",
                to="tournaments.standingruleset",
            ),
        ),
        migrations.RunPython(seed_standing_rule_sets, migrations.RunPython.noop),
    ]
