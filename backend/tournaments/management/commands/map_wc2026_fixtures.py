from django.core.management.base import BaseCommand

from tournaments.services.wc2026_fixture_mapping import (
    DEFAULT_LEAGUE_ID,
    DEFAULT_SEASON,
    map_wc2026_group_fixtures,
)


class Command(BaseCommand):
    help = "Map FIFA World Cup 2026 group matches to API-Football fixture IDs."

    def add_arguments(self, parser):
        parser.add_argument("--league-id", type=int, default=DEFAULT_LEAGUE_ID)
        parser.add_argument("--season", type=int, default=DEFAULT_SEASON)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        result = map_wc2026_group_fixtures(
            league_id=options["league_id"],
            season=options["season"],
            dry_run=options["dry_run"],
        )
        if not result.get("ok"):
            error = result.get("error", "unknown")
            if error == "tournament_not_found":
                self.stderr.write("World Cup 2026 tournament not found. Run seed_data first.")
            elif error == "missing_api_key":
                self.stderr.write("API_FOOTBALL_KEY is not set.")
            else:
                self.stderr.write(f"Mapping failed: {result.get('detail') or error}")
            return

        self.stdout.write(f"Fetched {result['fixtures_fetched']} fixtures from API-Football.")
        for sample in result.get("samples", []):
            self.stdout.write(
                f"Mapped {sample['match']} → {sample['fixture_id']}"
            )
        self.stdout.write(
            self.style.SUCCESS(
                f"Done: mapped={result['mapped']}, unmatched={result['unmatched']}, "
                f"ambiguous={result['ambiguous']}"
                + (" (dry run)" if result.get("dry_run") else "")
            )
        )
