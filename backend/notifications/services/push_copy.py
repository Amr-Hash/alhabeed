from __future__ import annotations

from typing import Any


def _rank_change_text(rank: Any, previous: Any) -> str:
    if rank is None:
        return ""
    if previous is None:
        return " (new)"
    try:
        delta = int(previous) - int(rank)
    except (TypeError, ValueError):
        return ""
    if delta > 0:
        return f" (↑{delta})"
    if delta < 0:
        return f" (↓{abs(delta)})"
    return ""


def match_result_push_copy(payload: dict[str, Any]) -> tuple[str, str]:
    home = payload.get("home_team") or "Home"
    away = payload.get("away_team") or "Away"
    score = f"{payload.get('home_score')}-{payload.get('away_score')}"
    pick = f"{payload.get('predicted_home_score')}-{payload.get('predicted_away_score')}"
    points = payload.get("points_awarded", 0)
    rank = payload.get("global_rank")
    rank_text = f"#{rank}" if rank is not None else "—"
    rank_change = _rank_change_text(rank, payload.get("previous_global_rank"))
    title = f"{home} {score} {away}"
    body = f"Your pick: {pick}. +{points} pts. Global rank: {rank_text}{rank_change}."
    return title, body


def group_podium_push_copy(payload: dict[str, Any]) -> tuple[str, str]:
    group = payload.get("group_name") or "Group"
    medals = ("🥇", "🥈", "🥉")
    by_rank: dict[int, list[str]] = {}
    for entry in payload.get("podium") or []:
        rank = entry.get("rank")
        username = entry.get("username")
        if rank is None or username is None or rank < 1 or rank > 3:
            continue
        by_rank.setdefault(rank, []).append(username)

    parts: list[str] = []
    for rank in (1, 2, 3):
        names = by_rank.get(rank)
        if names:
            parts.append(f"{medals[rank - 1]} {', '.join(names)}")

    podium = " · ".join(parts) if parts else "Updated"
    title = f"{group} podium updated"
    body = f"Top 3: {podium}"
    return title, body
