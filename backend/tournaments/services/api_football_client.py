from __future__ import annotations

import os
from typing import Any

import requests

API_FOOTBALL_BASE = "https://v3.football.api-sports.io"


def api_football_headers() -> dict[str, str]:
    api_key = os.environ.get("API_FOOTBALL_KEY", "").strip()
    if not api_key:
        raise ValueError("API_FOOTBALL_KEY is not set")
    return {"x-apisports-key": api_key}


def fetch_season_fixtures(league_id: int, season: int) -> list[dict[str, Any]]:
    """Fetch all fixtures for a league season (paginated)."""
    headers = api_football_headers()
    fixtures: list[dict[str, Any]] = []
    page = 1
    total_pages = 1

    while page <= total_pages:
        res = requests.get(
            f"{API_FOOTBALL_BASE}/fixtures",
            headers=headers,
            params={"league": league_id, "season": season, "page": page},
            timeout=30,
        )
        res.raise_for_status()
        body = res.json()
        fixtures.extend(body.get("response") or [])
        paging = body.get("paging") or {}
        total_pages = int(paging.get("total") or 1)
        page += 1

    return fixtures


def fetch_fixtures_by_ids(fixture_ids: list[str | int]) -> tuple[list[dict[str, Any]], int]:
    """
    Fetch fixture payloads by ID (max 20 IDs per request).
    Returns (fixtures, api_request_count).
    """
    ids = [str(item).strip() for item in fixture_ids if str(item).strip()]
    if not ids:
        return [], 0

    headers = api_football_headers()
    fixtures: list[dict[str, Any]] = []
    api_requests = 0

    for start in range(0, len(ids), 20):
        chunk = ids[start : start + 20]
        res = requests.get(
            f"{API_FOOTBALL_BASE}/fixtures",
            headers=headers,
            params={"ids": "-".join(chunk)},
            timeout=30,
        )
        res.raise_for_status()
        body = res.json()
        fixtures.extend(body.get("response") or [])
        api_requests += 1

    return fixtures, api_requests
