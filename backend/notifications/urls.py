from django.urls import path

from .views import (
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
    PushSubscribeView,
    PushUnsubscribeView,
    PushVapidPublicKeyView,
)

urlpatterns = [
    path("", NotificationListView.as_view(), name="notification-list"),
    path("mark-all-read", NotificationMarkAllReadView.as_view(), name="notification-mark-all-read"),
    path("push/vapid-public-key", PushVapidPublicKeyView.as_view(), name="push-vapid-public-key"),
    path("push/subscribe", PushSubscribeView.as_view(), name="push-subscribe"),
    path("push/unsubscribe", PushUnsubscribeView.as_view(), name="push-unsubscribe"),
    path("<int:pk>/read", NotificationMarkReadView.as_view(), name="notification-mark-read"),
]
