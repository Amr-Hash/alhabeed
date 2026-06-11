from django.conf import settings
from django.db import models


class Prediction(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="predictions",
    )
    group = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="predictions",
    )
    match = models.ForeignKey(
        "tournaments.Match",
        on_delete=models.CASCADE,
        related_name="predictions",
    )
    predicted_home_score = models.PositiveSmallIntegerField()
    predicted_away_score = models.PositiveSmallIntegerField()
    predicted_winner_team = models.ForeignKey(
        "tournaments.Team",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="predicted_wins",
    )
    points_awarded = models.PositiveSmallIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "group", "match")
        indexes = [
            models.Index(fields=["user", "group"]),
            models.Index(fields=["group", "match"]),
            models.Index(fields=["match"]),
            models.Index(fields=["user", "points_awarded"]),
            models.Index(fields=["group", "user", "points_awarded"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.match} ({self.group.name})"
