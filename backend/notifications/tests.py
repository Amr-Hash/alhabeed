from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from notifications.models import Notification
from notifications.services.match_reminders import send_match_kickoff_reminders
from predictions.models import Prediction
from tournaments.models import Match, Stage, Team, Tournament, TournamentSubscription

User = get_user_model()


class MatchKickoffReminderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="fan1", email="fan1@test.com", password="pass12345"
        )
        self.other = User.objects.create_user(
            username="fan2", email="fan2@test.com", password="pass12345"
        )
        self.tournament = Tournament.objects.create(
            name="Test Cup",
            year=2026,
            start_date="2026-06-01",
            end_date="2026-07-01",
            is_active=True,
        )
        self.stage = Stage.objects.create(
            tournament=self.tournament,
            name="Group Day 1",
            order=1,
            stage_type=Stage.StageType.GROUP,
        )
        self.home = Team.objects.create(name="Home FC", code="HFC")
        self.away = Team.objects.create(name="Away FC", code="AFC")
        self.kickoff = timezone.now() + timedelta(hours=1)
        self.match = Match.objects.create(
            tournament=self.tournament,
            stage=self.stage,
            home_team=self.home,
            away_team=self.away,
            kickoff_time=self.kickoff,
            status=Match.Status.SCHEDULED,
        )
        self.prediction = Prediction.objects.create(
            user=self.user,
            match=self.match,
            predicted_home_score=2,
            predicted_away_score=1,
        )
        TournamentSubscription.objects.create(user=self.user, tournament=self.tournament)
        TournamentSubscription.objects.create(user=self.other, tournament=self.tournament)

    @patch("notifications.services.match_reminders.send_push_to_user", return_value=1)
    def test_creates_reminder_with_prediction_payload(self, mock_push):
        result = send_match_kickoff_reminders()

        self.assertEqual(result["matches"], 1)
        self.assertEqual(result["created"], 2)
        notification = Notification.objects.get(
            user=self.user,
            dedup_key=f"match_kickoff_reminder:{self.match.id}",
        )
        self.assertEqual(
            notification.notification_type,
            Notification.Type.MATCH_KICKOFF_REMINDER,
        )
        self.assertTrue(notification.payload["has_prediction"])
        self.assertEqual(notification.payload["predicted_home_score"], 2)
        self.assertEqual(notification.payload["predicted_away_score"], 1)
        mock_push.assert_called()

    @patch("notifications.services.match_reminders.send_push_to_user", return_value=0)
    def test_dedup_skips_second_run(self, mock_push):
        send_match_kickoff_reminders()
        result = send_match_kickoff_reminders()

        self.assertEqual(result["created"], 0)
        self.assertEqual(
            Notification.objects.filter(
                notification_type=Notification.Type.MATCH_KICKOFF_REMINDER
            ).count(),
            2,
        )
        self.assertEqual(mock_push.call_count, 2)

    @patch("notifications.services.match_reminders.send_push_to_user", return_value=0)
    def test_no_prediction_payload_for_user_without_pick(self, mock_push):
        send_match_kickoff_reminders()

        notification = Notification.objects.get(
            user=self.other,
            dedup_key=f"match_kickoff_reminder:{self.match.id}",
        )
        self.assertFalse(notification.payload["has_prediction"])
        self.assertIsNone(notification.payload["predicted_home_score"])

    @patch("notifications.services.match_reminders.send_push_to_user", return_value=0)
    def test_skips_users_not_subscribed_to_tournament(self, mock_push):
        unsubscribed = User.objects.create_user(
            username="outsider",
            email="outsider@test.com",
            password="pass12345",
        )
        TournamentSubscription.objects.filter(user=unsubscribed).delete()
        send_match_kickoff_reminders()
        self.assertFalse(
            Notification.objects.filter(
                user=unsubscribed,
                dedup_key=f"match_kickoff_reminder:{self.match.id}",
            ).exists()
        )

    @patch("notifications.services.match_reminders.send_push_to_user", return_value=0)
    def test_ignores_matches_outside_window(self, mock_push):
        self.match.kickoff_time = timezone.now() + timedelta(hours=3)
        self.match.save(update_fields=["kickoff_time"])

        result = send_match_kickoff_reminders()

        self.assertEqual(result["matches"], 0)
        self.assertEqual(Notification.objects.count(), 0)
