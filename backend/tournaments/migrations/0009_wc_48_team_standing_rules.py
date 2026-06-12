from django.db import migrations


def sync_wc_standing_rules(apps, schema_editor):
    from tournaments.services.standing_rule_sets import (
        sync_builtin_rule_sets,
        sync_world_cup_tournaments,
    )

    sync_builtin_rule_sets()
    sync_world_cup_tournaments()


class Migration(migrations.Migration):

    dependencies = [
        ("tournaments", "0008_tournament_subscriptions"),
    ]

    operations = [
        migrations.RunPython(sync_wc_standing_rules, migrations.RunPython.noop),
    ]
