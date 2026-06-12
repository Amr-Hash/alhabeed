from django.conf import settings
from django.db import models


class PushSubscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_subscriptions",
    )
    endpoint = models.TextField(unique=True)
    p256dh = models.CharField(max_length=255)
    auth = models.CharField(max_length=255)
    user_agent = models.CharField(max_length=255, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user", "-updated_at"])]

    def as_subscription_info(self) -> dict:
        return {
            "endpoint": self.endpoint,
            "keys": {"p256dh": self.p256dh, "auth": self.auth},
        }

    def __str__(self):
        return f"PushSubscription user={self.user_id}"


class Notification(models.Model):
    class Type(models.TextChoices):
        MATCH_RESULT = "match_result", "Match result"
        GROUP_PODIUM = "group_podium", "Group podium change"
        MATCH_KICKOFF_REMINDER = "match_kickoff_reminder", "Match kickoff reminder"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(max_length=32, choices=Type.choices)
    dedup_key = models.CharField(max_length=128, blank=True, default="")
    payload = models.JSONField(default=dict)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read", "-created_at"]),
            models.Index(fields=["user", "dedup_key"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "dedup_key"],
                condition=~models.Q(dedup_key=""),
                name="notifications_unique_user_dedup_key",
            ),
        ]

    def __str__(self):
        return f"{self.notification_type} → {self.user_id}"
