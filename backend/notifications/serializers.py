from rest_framework import serializers

from .models import Notification


class PushSubscribeSerializer(serializers.Serializer):
    endpoint = serializers.CharField()
    p256dh = serializers.CharField()
    auth = serializers.CharField()


class PushUnsubscribeSerializer(serializers.Serializer):
    endpoint = serializers.CharField()


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = (
            "id",
            "notification_type",
            "payload",
            "is_read",
            "created_at",
        )
        read_only_fields = fields
