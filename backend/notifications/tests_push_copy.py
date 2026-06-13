from django.test import TestCase

from notifications.services.push_copy import group_podium_push_copy, match_result_push_copy


class PushCopyTests(TestCase):
    def test_match_result_push_copy(self):
        title, body = match_result_push_copy(
            {
                "home_team": "Egypt",
                "away_team": "Morocco",
                "home_score": 2,
                "away_score": 1,
                "predicted_home_score": 2,
                "predicted_away_score": 1,
                "points_awarded": 5,
                "global_rank": 3,
                "previous_global_rank": 5,
            }
        )
        self.assertEqual(title, "Egypt 2-1 Morocco")
        self.assertIn("+5 pts", body)
        self.assertIn("#3", body)
        self.assertIn("(↑2)", body)

    def test_group_podium_push_copy(self):
        title, body = group_podium_push_copy(
            {
                "group_name": "Friends",
                "podium": [
                    {"rank": 1, "username": "alice"},
                    {"rank": 2, "username": "bob"},
                    {"rank": 3, "username": "carol"},
                ],
            }
        )
        self.assertEqual(title, "Friends podium updated")
        self.assertIn("alice", body)
        self.assertIn("bob", body)
        self.assertIn("carol", body)
