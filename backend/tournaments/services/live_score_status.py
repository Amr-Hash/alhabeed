from __future__ import annotations

import os
from typing import Any

from django.db.models import Count, Q
from django.utils import timezone

from tournaments.models import Match, Tournament
from tournaments.services.live_scores import SYNC_WINDOW_AFTER, SYNC_WINDOW_BEFORE, is_sync_window_open


def get_global_live_score_environment() -> dict[str, Any]:
    start = os.environ.get("LIVE_SCORE_SYNC_START", "").strip() or None
    end = os.environ.get("LIVE_SCORE_SYNC_END", "").strip() or None
    return {
        "api_football_key_configured": bool(os.environ.get("API_FOOTBALL_KEY", "").strip()),
        "sportmonks_key_configured": bool(os.environ.get("SPORTMONKS_API_KEY", "").strip()),
        "cron_secret_configured": bool(os.environ.get("CRON_SECRET", "").strip()),
        "sync_window_open": is_sync_window_open(),
        "sync_window_start": start,
        "sync_window_end": end,
        "cron_schedule": "every_5_minutes",
    }


def _config_issues(tournament: Tournament) -> list[str]:
    provider = tournament.live_score_provider
    if provider == Tournament.LiveScoreProvider.MANUAL:
        return []

    config = tournament.live_score_config or {}
    issues: list[str] = []

    if provider == Tournament.LiveScoreProvider.API_FOOTBALL:
        if not os.environ.get("API_FOOTBALL_KEY", "").strip():
            issues.append("missing_api_key")
        if not config.get("league_id") or not config.get("season"):
            issues.append("missing_config")
    elif provider == Tournament.LiveScoreProvider.SPORTMONKS:
        if not os.environ.get("SPORTMONKS_API_KEY", "").strip():
            issues.append("missing_api_key")
        if not config.get("season_id"):
            issues.append("missing_config")
        issues.append("provider_not_implemented")

    if not is_sync_window_open():
        issues.append("outside_sync_window")

    return issues


def _health_status(tournament: Tournament, issues: list[str], unmapped_non_finished: int) -> str:
    if tournament.live_score_provider == Tournament.LiveScoreProvider.MANUAL:
        return "manual"
    blocking = {
        issue
        for issue in issues
        if issue in {"missing_api_key", "missing_config", "provider_not_implemented"}
    }
    if blocking:
        return "error"
    if unmapped_non_finished > 0 or "outside_sync_window" in issues:
        return "warning"
    return "ready"


def get_tournament_live_score_status(
    tournament: Tournament,
    *,
    detailed: bool = False,
) -> dict[str, Any]:
    now = timezone.now()
    matches = Match.objects.filter(tournament=tournament)
    status_counts = {
        row["status"]: row["count"]
        for row in matches.values("status").annotate(count=Count("id"))
    }
    total_matches = sum(status_counts.values())
    mapped_matches = matches.exclude(external_fixture_id="").count()
    unmapped_non_finished = matches.filter(
        Q(external_fixture_id="") | Q(external_fixture_id__isnull=True),
        status__in=[Match.Status.SCHEDULED, Match.Status.LIVE],
    ).count()

    sync_window_matches = 0
    for match in matches.exclude(status=Match.Status.FINISHED).iterator():
        if match.status == Match.Status.LIVE:
            sync_window_matches += 1
            continue
        start = match.kickoff_time - SYNC_WINDOW_BEFORE
        end = match.kickoff_time + SYNC_WINDOW_AFTER
        if start <= now <= end:
            sync_window_matches += 1

    issues = _config_issues(tournament)
    if (
        tournament.live_score_provider != Tournament.LiveScoreProvider.MANUAL
        and unmapped_non_finished > 0
    ):
        issues.append("unmapped_fixtures")

    payload: dict[str, Any] = {
        "tournament_id": tournament.id,
        "tournament_name": tournament.name,
        "tournament_name_ar": tournament.name_ar,
        "year": tournament.year,
        "is_active": tournament.is_active,
        "is_archived": tournament.is_archived,
        "live_score_provider": tournament.live_score_provider,
        "live_score_config": tournament.live_score_config or {},
        "health": _health_status(tournament, issues, unmapped_non_finished),
        "issues": issues,
        "matches": {
            "total": total_matches,
            "scheduled": status_counts.get(Match.Status.SCHEDULED, 0),
            "live": status_counts.get(Match.Status.LIVE, 0),
            "finished": status_counts.get(Match.Status.FINISHED, 0),
            "mapped_fixtures": mapped_matches,
            "unmapped_active": unmapped_non_finished,
            "in_sync_window": sync_window_matches,
        },
    }

    if detailed:
        unmapped = (
            matches.filter(
                Q(external_fixture_id="") | Q(external_fixture_id__isnull=True),
                status__in=[Match.Status.SCHEDULED, Match.Status.LIVE],
            )
            .select_related("home_team", "away_team")
            .order_by("kickoff_time")[:25]
        )
        payload["unmapped_matches"] = [
            {
                "id": match.id,
                "home_team": match.home_team.name,
                "away_team": match.away_team.name,
                "kickoff_time": match.kickoff_time.isoformat(),
                "status": match.status,
            }
            for match in unmapped
        ]

    return payload


def get_live_score_overview() -> dict[str, Any]:
    tournaments = [
        get_tournament_live_score_status(tournament)
        for tournament in Tournament.objects.all().order_by("-year", "name")
    ]
    auto_sync_count = sum(
        1
        for row in tournaments
        if row["live_score_provider"] != Tournament.LiveScoreProvider.MANUAL
    )
    return {
        "environment": get_global_live_score_environment(),
        "summary": {
            "tournament_count": len(tournaments),
            "auto_sync_tournament_count": auto_sync_count,
            "ready_count": sum(1 for row in tournaments if row["health"] == "ready"),
            "warning_count": sum(1 for row in tournaments if row["health"] == "warning"),
            "error_count": sum(1 for row in tournaments if row["health"] == "error"),
        },
        "tournaments": tournaments,
    }
