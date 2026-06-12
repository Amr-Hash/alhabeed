from __future__ import annotations

from django.db.models import Q, QuerySet

from tournaments.models import Continent, Team, Tournament


def default_team_eligibility_for_competition(competition_type: str) -> dict[str, str]:
    from tournaments.models import StandingRuleSet

    if competition_type == StandingRuleSet.CompetitionType.WORLD_CUP:
        return {
            "allowed_team_type": Tournament.AllowedTeamType.NATIONAL,
            "team_scope": Tournament.TeamScope.WORLDWIDE,
            "allowed_continent": "",
            "allowed_country_code": "",
            "allowed_division": "",
        }
    if competition_type == StandingRuleSet.CompetitionType.CHAMPIONS_LEAGUE:
        return {
            "allowed_team_type": Tournament.AllowedTeamType.CLUB,
            "team_scope": Tournament.TeamScope.CONTINENT,
            "allowed_continent": Continent.EUROPE,
            "allowed_country_code": "",
            "allowed_division": "",
        }
    return {
        "allowed_team_type": Tournament.AllowedTeamType.ANY,
        "team_scope": Tournament.TeamScope.WORLDWIDE,
        "allowed_continent": "",
        "allowed_country_code": "",
        "allowed_division": "",
    }


def apply_team_eligibility_defaults(
    attrs: dict,
    *,
    instance: Tournament | None = None,
) -> dict:
    competition_type = attrs.get("competition_type")
    if instance and competition_type is None:
        competition_type = instance.competition_type
    if not competition_type:
        return attrs

    defaults = default_team_eligibility_for_competition(competition_type)
    for key, value in defaults.items():
        if key not in attrs and (instance is None or not getattr(instance, key, None)):
            attrs[key] = value
    return attrs


def team_type_allowed(team: Team, tournament: Tournament) -> bool:
    allowed = tournament.allowed_team_type
    if allowed == Tournament.AllowedTeamType.ANY:
        return True
    if allowed == Tournament.AllowedTeamType.NATIONAL:
        return team.team_type == Team.TeamType.NATIONAL
    if allowed == Tournament.AllowedTeamType.CLUB:
        return team.team_type == Team.TeamType.CLUB
    return True


def team_scope_allowed(team: Team, tournament: Tournament) -> bool:
    scope = tournament.team_scope
    if scope == Tournament.TeamScope.WORLDWIDE:
        return True
    if scope == Tournament.TeamScope.CONTINENT:
        return (
            bool(tournament.allowed_continent)
            and team.continent == tournament.allowed_continent
        )
    if scope == Tournament.TeamScope.COUNTRY:
        return (
            bool(tournament.allowed_country_code)
            and team.country_code.lower() == tournament.allowed_country_code.lower()
        )
    if scope == Tournament.TeamScope.DIVISION:
        if not tournament.allowed_division:
            return False
        return team.division.lower() == tournament.allowed_division.lower()
    return True


def team_eligible_for_tournament(team: Team, tournament: Tournament) -> bool:
    return team_type_allowed(team, tournament) and team_scope_allowed(team, tournament)


def ineligibility_reason(team: Team, tournament: Tournament) -> str | None:
    if not team_type_allowed(team, tournament):
        if tournament.allowed_team_type == Tournament.AllowedTeamType.NATIONAL:
            return "Only national teams (countries) are allowed in this tournament."
        if tournament.allowed_team_type == Tournament.AllowedTeamType.CLUB:
            return "Only club teams are allowed in this tournament."
        return "This team type is not allowed in this tournament."

    if not team_scope_allowed(team, tournament):
        if tournament.team_scope == Tournament.TeamScope.CONTINENT:
            return f"Only teams from continent '{tournament.allowed_continent}' are allowed."
        if tournament.team_scope == Tournament.TeamScope.COUNTRY:
            return f"Only teams from country '{tournament.allowed_country_code}' are allowed."
        if tournament.team_scope == Tournament.TeamScope.DIVISION:
            return f"Only teams from division '{tournament.allowed_division}' are allowed."
        return "This team is outside the tournament's geographic scope."
    return None


def validate_team_for_tournament(team: Team, tournament: Tournament) -> None:
    reason = ineligibility_reason(team, tournament)
    if reason:
        raise ValueError(f"{team.name} ({team.code}): {reason}")


def validate_team_ids_for_tournament(team_ids: list[int], tournament: Tournament) -> None:
    teams = Team.objects.filter(id__in=team_ids)
    found = {team.id for team in teams}
    missing = set(team_ids) - found
    if missing:
        raise ValueError(f"Unknown team id(s): {sorted(missing)}")
    errors: list[str] = []
    for team in teams:
        reason = ineligibility_reason(team, tournament)
        if reason:
            errors.append(f"{team.name} ({team.code}): {reason}")
    if errors:
        raise ValueError("; ".join(errors))


def eligible_teams_for_tournament(tournament: Tournament) -> QuerySet[Team]:
    qs = Team.objects.all()
    allowed = tournament.allowed_team_type
    if allowed == Tournament.AllowedTeamType.NATIONAL:
        qs = qs.filter(team_type=Team.TeamType.NATIONAL)
    elif allowed == Tournament.AllowedTeamType.CLUB:
        qs = qs.filter(team_type=Team.TeamType.CLUB)

    scope = tournament.team_scope
    if scope == Tournament.TeamScope.CONTINENT and tournament.allowed_continent:
        qs = qs.filter(continent=tournament.allowed_continent)
    elif scope == Tournament.TeamScope.COUNTRY and tournament.allowed_country_code:
        qs = qs.filter(country_code__iexact=tournament.allowed_country_code)
    elif scope == Tournament.TeamScope.DIVISION and tournament.allowed_division:
        qs = qs.filter(division__iexact=tournament.allowed_division)

    return qs.order_by("name")
