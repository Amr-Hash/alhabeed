"""Fetch live scores from football-data.org (v4 API)."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any

import requests

from tournaments.models import Match
from tournaments.services.datetime_utils import ensure_aware_datetime
from tournaments.services.team_name_matching import (
    build_code_lookup,
    normalize_team_name,
    scraped_team_name_to_code,
)

logger = logging.getLogger(__name__)

API_BASE = "https://api.football-data.org/v4"
DEFAULT_COMPETITION_CODE = "WC"

# football-data.org TLA → our Team.code when they differ.
TLA_CODE_OVERRIDES: dict[str, str] = {
    "CUR": "CUW",
}


@dataclass(frozen=True)
class FootballDataMatch:
    home_code: str | None
    away_code: str | None
    home_name: str
    away_name: str
    home_score: int | None
    away_score: int | None
    status: str
    utc_date: datetime | None


def resolve_api_token() -> str:
    return os.environ.get("FOOTBALL_DATA_API_TOKEN", "").strip()


def resolve_competition_code(config: dict[str, Any] | None) -> str:
    config = config or {}
    code = str(config.get("competition_code") or "").strip().upper()
    if code:
        return code
    env_code = os.environ.get("FOOTBALL_DATA_COMPETITION_CODE", "").strip().upper()
    return env_code or DEFAULT_COMPETITION_CODE


def resolve_season(config: dict[str, Any] | None, tournament_year: int | None) -> int | None:
    config = config or {}
    raw = config.get("season")
    if raw is not None and str(raw).strip():
        try:
            return int(raw)
        except (TypeError, ValueError):
            logger.warning("Ignoring invalid football_data season value: %r", raw)
    if tournament_year:
        return int(tournament_year)
    return None


def fetch_competition_matches(
    *,
    competition_code: str,
    season: int | None,
    date_from: date,
    date_to: date,
    api_token: str | None = None,
) -> list[FootballDataMatch]:
    token = (api_token or resolve_api_token()).strip()
    if not token:
        raise ValueError("missing_api_token")

    params: dict[str, str] = {
        "dateFrom": date_from.isoformat(),
        "dateTo": date_to.isoformat(),
    }
    if season is not None:
        params["season"] = str(season)

    headers = {
        "X-Auth-Token": token,
        "User-Agent": "AlhabeedLiveScores/1.0 (+https://alhabeed.vercel.app)",
    }
    url = f"{API_BASE}/competitions/{competition_code}/matches"
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()
    items = payload.get("matches") if isinstance(payload, dict) else None
    if not isinstance(items, list):
        return []

    lookup = build_code_lookup()
    rows: list[FootballDataMatch] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        parsed = _parse_match_item(item, lookup)
        if parsed:
            rows.append(parsed)
    return rows


def find_football_data_match_for_match(
    match: Match,
    api_matches: list[FootballDataMatch],
) -> FootballDataMatch | None:
    home_code = match.home_team.code.upper()
    away_code = match.away_team.code.upper()
    home_name = match.home_team.name
    away_name = match.away_team.name
    kickoff = ensure_aware_datetime(match.kickoff_time) if match.kickoff_time else None

    best: FootballDataMatch | None = None
    best_delta = timedelta(hours=6)

    for row in api_matches:
        if not _teams_match(row, home_code, away_code, home_name, away_name):
            continue
        if kickoff and row.utc_date:
            delta = abs(row.utc_date - kickoff)
            if delta < best_delta:
                best = row
                best_delta = delta
        elif best is None:
            best = row

    return best


def _teams_match(
    row: FootballDataMatch,
    home_code: str,
    away_code: str,
    home_name: str,
    away_name: str,
) -> bool:
    if row.home_code == home_code and row.away_code == away_code:
        return True
    return (
        normalize_team_name(row.home_name) == normalize_team_name(home_name)
        and normalize_team_name(row.away_name) == normalize_team_name(away_name)
    )


def _parse_match_item(item: dict[str, Any], lookup: dict[str, str]) -> FootballDataMatch | None:
    home = item.get("homeTeam") or {}
    away = item.get("awayTeam") or {}
    if not isinstance(home, dict) or not isinstance(away, dict):
        return None

    home_name = str(home.get("name") or home.get("shortName") or "").strip()
    away_name = str(away.get("name") or away.get("shortName") or "").strip()
    if not home_name or not away_name:
        return None

    home_code = _team_code_from_api(home, home_name, lookup)
    away_code = _team_code_from_api(away, away_name, lookup)
    home_score, away_score = _extract_scores(item)
    status = _map_external_status(item.get("status"))
    utc_date = _parse_utc_date(item.get("utcDate"))

    return FootballDataMatch(
        home_code=home_code,
        away_code=away_code,
        home_name=home_name,
        away_name=away_name,
        home_score=home_score,
        away_score=away_score,
        status=status,
        utc_date=utc_date,
    )


def _team_code_from_api(team: dict[str, Any], name: str, lookup: dict[str, str]) -> str | None:
    tla = str(team.get("tla") or "").strip().upper()
    if tla:
        return TLA_CODE_OVERRIDES.get(tla, tla)
    return scraped_team_name_to_code(name, lookup)


def _extract_scores(item: dict[str, Any]) -> tuple[int | None, int | None]:
    score = item.get("score")
    if not isinstance(score, dict):
        return None, None

    full_time = score.get("fullTime")
    if isinstance(full_time, dict):
        home = _coerce_score(full_time.get("home"))
        away = _coerce_score(full_time.get("away"))
        if home is not None or away is not None:
            return home, away

    regular_time = score.get("regularTime")
    if isinstance(regular_time, dict):
        home = _coerce_score(regular_time.get("home"))
        away = _coerce_score(regular_time.get("away"))
        if home is not None or away is not None:
            return home, away

    return None, None


def _coerce_score(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _parse_utc_date(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None


def _map_external_status(value: Any) -> str:
    if value is None:
        return Match.Status.SCHEDULED
    text = str(value).strip().upper()
    if text in {"LIVE", "IN_PLAY", "PAUSED", "SUSPENDED"}:
        return Match.Status.LIVE
    if text == "FINISHED":
        return Match.Status.FINISHED
    return Match.Status.SCHEDULED
