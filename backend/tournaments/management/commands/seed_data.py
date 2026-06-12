from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from tournaments.ar_translations import (
    WC2026_TOURNAMENT_AR,
    cup_group_name_ar,
    stage_name_ar,
    team_name_ar,
)
from tournaments.models import CupGroup, CupGroupTeam, Match, Stage, Team, Tournament
from tournaments.services.standing_rule_sets import (
    sync_builtin_rule_sets,
    sync_world_cup_tournaments,
)
from tournaments.services.team_geography import geography_for_team_code
from tournaments.wc2026_data import (
    WC2026_GROUP_MATCHES,
    WC2026_GROUPS,
    WC2026_TEAMS,
    WC2026_TOURNAMENT,
)

User = get_user_model()

STAGES_CONFIG = [
    ("Group Stage", 1, Stage.StageType.GROUP),
    ("Round of 32", 4, Stage.StageType.KNOCKOUT),
    ("Round of 16", 5, Stage.StageType.KNOCKOUT),
    ("Quarter Finals", 6, Stage.StageType.KNOCKOUT),
    ("Semi Finals", 7, Stage.StageType.KNOCKOUT),
    ("Third Place Match", 8, Stage.StageType.KNOCKOUT),
    ("Final", 9, Stage.StageType.KNOCKOUT),
]


class Command(BaseCommand):
    help = "Seed tournament data and admin account for الهبيد (Al-Habeed)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        admin, _ = User.objects.get_or_create(
            email="admin@alhabeed.com",
            defaults={"username": "admin", "is_staff": True, "is_superuser": True},
        )
        admin.username = admin.username or "admin"
        admin.is_staff = True
        admin.is_superuser = True
        admin.is_active = True
        admin.set_password("admin12345")
        admin.save()

        teams = self._seed_teams(WC2026_TEAMS)
        wc_count = self._seed_wc_tournament(teams)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully!"))
        self.stdout.write(f"FIFA World Cup (2026): {wc_count} group-stage matches")
        self.stdout.write("Admin: admin@alhabeed.com / admin12345")

    def _seed_teams(self, team_rows):
        teams = {}
        for name, code, flag_iso in team_rows:
            flag_url = f"https://flagcdn.com/w80/{flag_iso}.png"
            geo = geography_for_team_code(code, flag_iso)
            team, _ = Team.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "name_ar": team_name_ar(code, name),
                    "flag_url": flag_url,
                    "team_type": geo["team_type"],
                    "country_code": geo["country_code"],
                    "continent": geo["continent"],
                },
            )
            teams[code] = team
        return teams

    def _create_stages(self, tournament, stages_config):
        stages = {}
        for name, order, stage_type in stages_config:
            stage, _ = Stage.objects.update_or_create(
                tournament=tournament,
                order=order,
                defaults={
                    "name": name,
                    "name_ar": stage_name_ar(name),
                    "stage_type": stage_type,
                },
            )
            stages[order] = stage
        return stages

    def _create_cup_groups(self, tournament, group_map, teams):
        cup_groups = {}
        for letter, team_codes in group_map.items():
            cup_group, _ = CupGroup.objects.update_or_create(
                tournament=tournament,
                name=letter,
                defaults={"name_ar": cup_group_name_ar(letter)},
            )
            if not cup_group.name_ar:
                cup_group.name_ar = cup_group_name_ar(letter)
                cup_group.save(update_fields=["name_ar"])
            cup_groups[letter] = cup_group
            CupGroupTeam.objects.filter(cup_group=cup_group).delete()
            for order, code in enumerate(team_codes):
                CupGroupTeam.objects.create(
                    cup_group=cup_group,
                    team=teams[code],
                    order=order,
                )
        return cup_groups

    def _seed_wc_tournament(self, teams):
        sync_builtin_rule_sets()
        tournament, created = Tournament.objects.update_or_create(
            name=WC2026_TOURNAMENT["name"],
            year=WC2026_TOURNAMENT["year"],
            defaults={
                "name_ar": WC2026_TOURNAMENT_AR,
                "start_date": WC2026_TOURNAMENT["start_date"],
                "end_date": WC2026_TOURNAMENT["end_date"],
            },
        )
        update_fields = []
        if created:
            tournament.is_active = True
            update_fields.append("is_active")
        if not tournament.name_ar:
            tournament.name_ar = WC2026_TOURNAMENT_AR
            update_fields.append("name_ar")
        if update_fields:
            tournament.save(update_fields=update_fields)
        sync_world_cup_tournaments()
        tournament.refresh_from_db()

        if Match.objects.filter(tournament=tournament).exists():
            return Match.objects.filter(tournament=tournament).count()

        stages = self._create_stages(tournament, STAGES_CONFIG)
        cup_groups = self._create_cup_groups(tournament, WC2026_GROUPS, teams)

        from tournaments.management.commands.sync_wc2026_kickoffs import parse_kickoff

        for group_letter, matchday, home_code, away_code, kickoff in WC2026_GROUP_MATCHES:
            if isinstance(kickoff, str):
                kickoff = parse_kickoff(kickoff)
            Match.objects.create(
                tournament=tournament,
                stage=stages[1],
                cup_group=cup_groups[group_letter],
                matchday=matchday,
                home_team=teams[home_code],
                away_team=teams[away_code],
                kickoff_time=kickoff,
            )
        return Match.objects.filter(tournament=tournament).count()
