from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from notifications.models import Notification
from notifications.services.push import frontend_base_url, send_push_to_user
from predictions.models import Prediction
from tournaments.models import Match, TournamentSubscription

User = get_user_model()

REMINDER_BEFORE = timedelta(hours=1)
REMINDER_WINDOW = timedelta(minutes=5)


def _reminder_payload(match: Match, prediction: Prediction | None) -> dict:
    payload = {
        "match_id": match.id,
        "tournament_id": match.tournament_id,
        "home_team": match.home_team.name,
        "away_team": match.away_team.name,
        "home_team_ar": getattr(match.home_team, "name_ar", None) or "",
        "away_team_ar": getattr(match.away_team, "name_ar", None) or "",
        "kickoff_time": match.kickoff_time.isoformat(),
        "has_prediction": prediction is not None,
        "predicted_home_score": None,
        "predicted_away_score": None,
        "predicted_winner_team_id": None,
        "predicted_winner_name": "",
        "predicted_winner_name_ar": "",
    }
    if prediction:
        payload["predicted_home_score"] = prediction.predicted_home_score
        payload["predicted_away_score"] = prediction.predicted_away_score
        if prediction.predicted_winner_team_id:
            winner = prediction.predicted_winner_team
            payload["predicted_winner_team_id"] = prediction.predicted_winner_team_id
            payload["predicted_winner_name"] = winner.name if winner else ""
            payload["predicted_winner_name_ar"] = (
                getattr(winner, "name_ar", None) or "" if winner else ""
            )
    return payload


def _push_copy(match: Match, prediction: Prediction | None) -> tuple[str, str]:
    home = match.home_team.name
    away = match.away_team.name
    if prediction:
        pick = f"{prediction.predicted_home_score}-{prediction.predicted_away_score}"
        title = f"{home} vs {away} in 1 hour"
        body = f"Kickoff soon. Your pick: {pick}. Tap to review or change it."
    else:
        title = f"{home} vs {away} in 1 hour"
        body = "Kickoff soon. You have not submitted a prediction yet."
    return title, body


def send_match_kickoff_reminders() -> dict:
    """
    Notify users 1 hour before kickoff (±2.5 min window for 5-minute cron).
    Creates in-app notifications once per user/match and sends Web Push when configured.
    """
    now = timezone.now()
    window_start = now + REMINDER_BEFORE - REMINDER_WINDOW / 2
    window_end = now + REMINDER_BEFORE + REMINDER_WINDOW / 2

    matches = list(
        Match.objects.filter(
            status=Match.Status.SCHEDULED,
            kickoff_time__gte=window_start,
            kickoff_time__lt=window_end,
            tournament__is_active=True,
            tournament__is_archived=False,
        ).select_related("home_team", "away_team", "tournament")
    )
    if not matches:
        return {"matches": 0, "created": 0, "push_sent": 0}

    match_ids = [match.id for match in matches]
    predictions = Prediction.objects.filter(match_id__in=match_ids).select_related(
        "predicted_winner_team"
    )
    prediction_by_user_match = {
        (row.user_id, row.match_id): row for row in predictions
    }

    created = 0
    push_sent = 0
    for match in matches:
        subscribed_user_ids = TournamentSubscription.objects.filter(
            tournament_id=match.tournament_id
        ).values_list("user_id", flat=True)
        users = list(
            User.objects.filter(
                id__in=subscribed_user_ids,
                is_active=True,
                is_staff=False,
            )
        )
        dedup_key = f"match_kickoff_reminder:{match.id}"
        match_url = f"{frontend_base_url()}/matches/{match.id}"
        for user in users:
            prediction = prediction_by_user_match.get((user.id, match.id))
            payload = _reminder_payload(match, prediction)
            notification, was_created = Notification.objects.get_or_create(
                user_id=user.id,
                dedup_key=dedup_key,
                defaults={
                    "notification_type": Notification.Type.MATCH_KICKOFF_REMINDER,
                    "payload": payload,
                    "is_read": False,
                },
            )
            if not was_created:
                continue
            created += 1
            title, body = _push_copy(match, prediction)
            push_sent += send_push_to_user(
                user.id,
                title=title,
                body=body,
                url=match_url,
            )

    return {"matches": len(matches), "created": created, "push_sent": push_sent}
