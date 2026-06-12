from __future__ import annotations

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from notifications.models import KickoffReminderSent, PushSubscription
from notifications.services.push import frontend_base_url, push_configured, send_push_to_user
from predictions.models import Prediction
from tournaments.models import Match, TournamentSubscription

User = get_user_model()

REMINDER_BEFORE = timedelta(hours=1)
REMINDER_WINDOW = timedelta(minutes=5)


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
    Web Push only: notify subscribed users 1 hour before kickoff (±2.5 min window).
    No-op when VAPID push is not configured on the server.
    """
    if not push_configured():
        return {
            "enabled": False,
            "matches": 0,
            "eligible_users": 0,
            "push_sent": 0,
        }

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
        return {"enabled": True, "matches": 0, "eligible_users": 0, "push_sent": 0}

    match_ids = [match.id for match in matches]
    predictions = Prediction.objects.filter(match_id__in=match_ids).select_related(
        "predicted_winner_team"
    )
    prediction_by_user_match = {
        (row.user_id, row.match_id): row for row in predictions
    }

    push_sent = 0
    eligible_users = 0
    for match in matches:
        subscribed_user_ids = set(
            TournamentSubscription.objects.filter(
                tournament_id=match.tournament_id
            ).values_list("user_id", flat=True)
        )
        push_user_ids = set(
            PushSubscription.objects.filter(user_id__in=subscribed_user_ids).values_list(
                "user_id", flat=True
            )
        )
        if not push_user_ids:
            continue

        already_sent = set(
            KickoffReminderSent.objects.filter(
                match_id=match.id, user_id__in=push_user_ids
            ).values_list("user_id", flat=True)
        )
        users = User.objects.filter(
            id__in=push_user_ids - already_sent,
            is_active=True,
            is_staff=False,
        )
        match_url = f"{frontend_base_url()}/matches/{match.id}"

        for user in users:
            eligible_users += 1
            prediction = prediction_by_user_match.get((user.id, match.id))
            title, body = _push_copy(match, prediction)
            sent = send_push_to_user(
                user.id,
                title=title,
                body=body,
                url=match_url,
            )
            if sent > 0:
                KickoffReminderSent.objects.get_or_create(user_id=user.id, match_id=match.id)
                push_sent += sent

    return {
        "enabled": True,
        "matches": len(matches),
        "eligible_users": eligible_users,
        "push_sent": push_sent,
    }
