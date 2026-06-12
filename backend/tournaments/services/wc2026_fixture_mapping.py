from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from tournaments.models import Match, Tournament
from tournaments.services.api_football_client import fetch_season_fixtures
from tournaments.services.api_football_mapping import api_team_name_to_code, build_code_lookup
from tournaments.services.datetime_utils import ensure_aware_datetime
from tournaments.wc2026_data import WC2026_TOURNAMENT

DEFAULT_LEAGUE_ID = 1
DEFAULT_SEASON = 2026
KICKOFF_TOLERANCE = timedelta(minutes=30)


def map_wc2026_group_fixtures(
    *,
    league_id: int = DEFAULT_LEAGUE_ID,
    season: int = DEFAULT_SEASON,
    dry_run: bool = False,
) -> dict[str, Any]:
    tournament = Tournament.objects.filter(
        name=WC2026_TOURNAMENT["name"],
        year=WC2026_TOURNAMENT["year"],
    ).first()
    if not tournament:
        return {"ok": False, "error": "tournament_not_found"}

    try:
        fixtures = fetch_season_fixtures(league_id, season)
    except ValueError:
        return {"ok": False, "error": "missing_api_key"}
    except Exception as exc:
        return {"ok": False, "error": "request_failed", "detail": str(exc)}

    lookup = build_code_lookup()
    matches = (
        Match.objects.filter(tournament=tournament, stage__stage_type="group")
        .select_related("home_team", "away_team")
        .order_by("kickoff_time")
    )

    mapped = 0
    unmatched = 0
    ambiguous = 0
    samples: list[dict[str, str]] = []

    for match in matches:
        candidates = []
        for item in fixtures:
            fixture = item.get("fixture") or {}
            kickoff_raw = fixture.get("date")
            if not kickoff_raw:
                continue
            kickoff = ensure_aware_datetime(
                datetime.fromisoformat(kickoff_raw.replace("Z", "+00:00"))
            )
            if abs(kickoff - match.kickoff_time) > KICKOFF_TOLERANCE:
                continue

            teams = item.get("teams") or {}
            home_name = (teams.get("home") or {}).get("name") or ""
            away_name = (teams.get("away") or {}).get("name") or ""
            home_code = api_team_name_to_code(home_name, lookup)
            away_code = api_team_name_to_code(away_name, lookup)
            if home_code == match.home_team.code and away_code == match.away_team.code:
                candidates.append(str(fixture["id"]))

        if len(candidates) == 1:
            ext_id = candidates[0]
            if not dry_run:
                match.external_fixture_id = ext_id
                match.save(update_fields=["external_fixture_id"])
            mapped += 1
            if len(samples) < 5:
                samples.append(
                    {
                        "match": f"{match.home_team.code} vs {match.away_team.code}",
                        "fixture_id": ext_id,
                    }
                )
        elif len(candidates) == 0:
            unmatched += 1
        else:
            ambiguous += 1

    if not dry_run:
        tournament.live_score_provider = Tournament.LiveScoreProvider.API_FOOTBALL
        tournament.live_score_config = {"league_id": league_id, "season": season}
        tournament.save(update_fields=["live_score_provider", "live_score_config"])

    return {
        "ok": True,
        "dry_run": dry_run,
        "fixtures_fetched": len(fixtures),
        "mapped": mapped,
        "unmatched": unmatched,
        "ambiguous": ambiguous,
        "tournament_id": tournament.id,
        "live_score_config": {"league_id": league_id, "season": season},
        "samples": samples,
    }
