from django.db import models


class Tournament(models.Model):
    name = models.CharField(max_length=200)
    year = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "name"]
        indexes = [
            models.Index(fields=["year"]),
            models.Index(fields=["is_archived"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.year})"


class Stage(models.Model):
    class StageType(models.TextChoices):
        GROUP = "group", "Group Stage"
        KNOCKOUT = "knockout", "Knockout Stage"

    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="stages"
    )
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField()
    stage_type = models.CharField(
        max_length=10, choices=StageType.choices, default=StageType.GROUP
    )

    class Meta:
        ordering = ["order"]
        unique_together = ("tournament", "order")
        indexes = [
            models.Index(fields=["tournament", "order"]),
        ]

    def __str__(self):
        return f"{self.tournament.name} - {self.name}"


class Team(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=3, unique=True)
    flag_url = models.URLField(blank=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["code"]),
        ]

    def __str__(self):
        return self.name


class Match(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        LIVE = "live", "Live"
        FINISHED = "finished", "Finished"

    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="matches"
    )
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE, related_name="matches")
    home_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="home_matches"
    )
    away_team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="away_matches"
    )
    kickoff_time = models.DateTimeField()
    status = models.CharField(
        max_length=10, choices=Status.choices, default=Status.SCHEDULED
    )
    home_score = models.PositiveSmallIntegerField(null=True, blank=True)
    away_score = models.PositiveSmallIntegerField(null=True, blank=True)
    winner_team = models.ForeignKey(
        Team,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="won_matches",
    )

    class Meta:
        ordering = ["kickoff_time"]
        indexes = [
            models.Index(fields=["tournament", "stage"]),
            models.Index(fields=["kickoff_time"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.home_team.code} vs {self.away_team.code}"

    @property
    def is_knockout(self):
        return self.stage.stage_type == Stage.StageType.KNOCKOUT

    @property
    def is_locked(self):
        from django.utils import timezone
        from django.conf import settings

        lock_time = self.kickoff_time - timezone.timedelta(
            hours=settings.PREDICTION_LOCK_HOURS
        )
        return timezone.now() >= lock_time
