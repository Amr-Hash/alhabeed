from django.core.management.base import BaseCommand

from tournaments.services.standing_rule_sets import (
    sync_builtin_rule_sets,
    sync_world_cup_tournaments,
)


class Command(BaseCommand):
    help = "Sync built-in standing rule sets and World Cup tournament defaults."

    def handle(self, *args, **options):
        rule_set_count = sync_builtin_rule_sets()
        tournament_count = sync_world_cup_tournaments()
        self.stdout.write(
            self.style.SUCCESS(
                f"Synced {rule_set_count} standing rule set(s); "
                f"updated {tournament_count} World Cup tournament(s)."
            )
        )
