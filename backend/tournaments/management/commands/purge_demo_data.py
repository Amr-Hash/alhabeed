from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from groups.models import Group
User = get_user_model()

DEMO_TOURNAMENT_NAME = "Demo Test Cup"
DEMO_USER_EMAILS = (
    "demo@alhabeed.com",
    "demo@worldcup.com",
)
DEMO_GROUP_NAME = "Demo Predictors"


class Command(BaseCommand):
    help = "Remove Demo Test Cup, demo accounts, and the Demo Predictors group."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without making changes.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        from tournaments.models import Tournament

        dry_run = options["dry_run"]
        demo_tournaments = Tournament.objects.filter(name=DEMO_TOURNAMENT_NAME)
        demo_groups = Group.objects.filter(name=DEMO_GROUP_NAME)
        demo_users = User.objects.filter(email__in=DEMO_USER_EMAILS)

        self.stdout.write(f"Demo tournaments: {demo_tournaments.count()}")
        self.stdout.write(f"Demo groups: {demo_groups.count()}")
        self.stdout.write(f"Demo users: {demo_users.count()}")

        if dry_run:
            for tournament in demo_tournaments:
                self.stdout.write(f"  would delete tournament: {tournament.name} ({tournament.year})")
            for group in demo_groups:
                self.stdout.write(f"  would delete group: {group.name}")
            for user in demo_users:
                self.stdout.write(f"  would delete user: {user.email}")
            return

        tournament_count, _ = demo_tournaments.delete()
        group_count, _ = demo_groups.delete()
        user_count, _ = demo_users.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Removed {tournament_count} tournament row(s), "
                f"{group_count} group row(s), {user_count} user row(s)."
            )
        )
