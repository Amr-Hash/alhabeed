from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from groups.models import Group, GroupMember
from tournaments.models import Match, Stage, Team, Tournament

User = get_user_model()

TEAMS = [
    ("Brazil", "BRA", "https://flagcdn.com/br.svg"),
    ("Argentina", "ARG", "https://flagcdn.com/ar.svg"),
    ("France", "FRA", "https://flagcdn.com/fr.svg"),
    ("Germany", "DEU", "https://flagcdn.com/de.svg"),
    ("Spain", "ESP", "https://flagcdn.com/es.svg"),
    ("England", "ENG", "https://flagcdn.com/gb-eng.svg"),
    ("Portugal", "POR", "https://flagcdn.com/pt.svg"),
    ("Netherlands", "NED", "https://flagcdn.com/nl.svg"),
    ("Italy", "ITA", "https://flagcdn.com/it.svg"),
    ("Belgium", "BEL", "https://flagcdn.com/be.svg"),
    ("Croatia", "CRO", "https://flagcdn.com/hr.svg"),
    ("Morocco", "MAR", "https://flagcdn.com/ma.svg"),
    ("Japan", "JPN", "https://flagcdn.com/jp.svg"),
    ("USA", "USA", "https://flagcdn.com/us.svg"),
    ("Mexico", "MEX", "https://flagcdn.com/mx.svg"),
    ("South Korea", "KOR", "https://flagcdn.com/kr.svg"),
    ("Uruguay", "URU", "https://flagcdn.com/uy.svg"),
    ("Colombia", "COL", "https://flagcdn.com/co.svg"),
    ("Ecuador", "ECU", "https://flagcdn.com/ec.svg"),
    ("Senegal", "SEN", "https://flagcdn.com/sn.svg"),
    ("Nigeria", "NGA", "https://flagcdn.com/ng.svg"),
    ("Ghana", "GHA", "https://flagcdn.com/gh.svg"),
    ("Cameroon", "CMR", "https://flagcdn.com/cm.svg"),
    ("Australia", "AUS", "https://flagcdn.com/au.svg"),
    ("Iran", "IRN", "https://flagcdn.com/ir.svg"),
    ("Saudi Arabia", "KSA", "https://flagcdn.com/sa.svg"),
    ("Canada", "CAN", "https://flagcdn.com/ca.svg"),
    ("Switzerland", "SUI", "https://flagcdn.com/ch.svg"),
    ("Denmark", "DEN", "https://flagcdn.com/dk.svg"),
    ("Poland", "POL", "https://flagcdn.com/pl.svg"),
    ("Serbia", "SRB", "https://flagcdn.com/rs.svg"),
    ("Wales", "WAL", "https://flagcdn.com/gb-wls.svg"),
]


class Command(BaseCommand):
    help = "Seed sample World Cup tournament data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        admin, _ = User.objects.get_or_create(
            email="admin@worldcup.com",
            defaults={"username": "admin", "is_staff": True, "is_superuser": True},
        )
        if not admin.has_usable_password():
            admin.set_password("admin12345")
            admin.save()

        demo, _ = User.objects.get_or_create(
            email="demo@worldcup.com",
            defaults={"username": "demo"},
        )
        if not demo.has_usable_password():
            demo.set_password("demo12345")
            demo.save()

        teams = {}
        for name, code, flag in TEAMS:
            team, _ = Team.objects.get_or_create(
                code=code, defaults={"name": name, "flag_url": flag}
            )
            teams[code] = team

        tournament, _ = Tournament.objects.get_or_create(
            name="FIFA World Cup",
            year=2026,
            defaults={
                "start_date": timezone.now().date(),
                "end_date": timezone.now().date() + timedelta(days=30),
            },
        )

        stages_config = [
            ("Group Stage Day 1", 1, Stage.StageType.GROUP),
            ("Group Stage Day 2", 2, Stage.StageType.GROUP),
            ("Group Stage Day 3", 3, Stage.StageType.GROUP),
            ("Round of 32", 4, Stage.StageType.KNOCKOUT),
            ("Round of 16", 5, Stage.StageType.KNOCKOUT),
            ("Quarter Finals", 6, Stage.StageType.KNOCKOUT),
            ("Semi Finals", 7, Stage.StageType.KNOCKOUT),
            ("Third Place Match", 8, Stage.StageType.KNOCKOUT),
            ("Final", 9, Stage.StageType.KNOCKOUT),
        ]

        stages = {}
        for name, order, stage_type in stages_config:
            stage, _ = Stage.objects.update_or_create(
                tournament=tournament,
                order=order,
                defaults={"name": name, "stage_type": stage_type},
            )
            stages[order] = stage

        team_codes = list(teams.keys())
        base_time = timezone.now() + timedelta(days=1)
        match_num = 0

        for day in [1, 2, 3]:
            stage = stages[day]
            for i in range(0, 8, 2):
                home = teams[team_codes[(match_num + i) % len(team_codes)]]
                away = teams[team_codes[(match_num + i + 1) % len(team_codes)]]
                Match.objects.get_or_create(
                    tournament=tournament,
                    stage=stage,
                    home_team=home,
                    away_team=away,
                    defaults={
                        "kickoff_time": base_time + timedelta(days=day - 1, hours=i),
                    },
                )
            match_num += 2

        round_of_32_pairs = [
            ("BRA", "URU"),
            ("ARG", "ECU"),
            ("FRA", "POL"),
            ("DEU", "SRB"),
            ("ESP", "COL"),
            ("ENG", "SEN"),
            ("POR", "GHA"),
            ("NED", "USA"),
            ("ITA", "AUS"),
            ("BEL", "JPN"),
            ("CRO", "MAR"),
            ("MEX", "KOR"),
            ("SUI", "CMR"),
            ("DEN", "NGA"),
            ("CAN", "IRN"),
            ("WAL", "KSA"),
        ]
        for i, (home_code, away_code) in enumerate(round_of_32_pairs):
            Match.objects.get_or_create(
                tournament=tournament,
                stage=stages[4],
                home_team=teams[home_code],
                away_team=teams[away_code],
                defaults={
                    "kickoff_time": base_time + timedelta(days=4, hours=i * 2),
                },
            )

        round_of_16_pairs = [
            ("BRA", "ARG"),
            ("FRA", "DEU"),
            ("ESP", "ENG"),
            ("POR", "NED"),
            ("ITA", "BEL"),
            ("CRO", "MAR"),
            ("JPN", "USA"),
            ("MEX", "KOR"),
        ]
        for i, (home_code, away_code) in enumerate(round_of_16_pairs):
            Match.objects.get_or_create(
                tournament=tournament,
                stage=stages[5],
                home_team=teams[home_code],
                away_team=teams[away_code],
                defaults={
                    "kickoff_time": base_time + timedelta(days=6, hours=i * 3),
                },
            )

        finished_match, created = Match.objects.get_or_create(
            tournament=tournament,
            stage=stages[1],
            home_team=teams["BRA"],
            away_team=teams["MEX"],
            defaults={
                "kickoff_time": timezone.now() - timedelta(days=1),
                "status": Match.Status.FINISHED,
                "home_score": 2,
                "away_score": 1,
            },
        )
        if not created and finished_match.status != Match.Status.FINISHED:
            finished_match.status = Match.Status.FINISHED
            finished_match.home_score = 2
            finished_match.away_score = 1
            finished_match.save()

        group, _ = Group.objects.get_or_create(
            name="Demo Predictors",
            defaults={"description": "Sample group for testing", "created_by": demo},
        )
        GroupMember.objects.get_or_create(
            group=group, user=demo, defaults={"role": GroupMember.Role.ADMIN}
        )
        GroupMember.objects.get_or_create(group=group, user=admin)

        self.stdout.write(self.style.SUCCESS("Seed data created successfully!"))
        self.stdout.write("Admin: admin@worldcup.com / admin12345")
        self.stdout.write("Demo:  demo@worldcup.com / demo12345")
