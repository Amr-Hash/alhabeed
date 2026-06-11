from django.urls import path

from .views import GlobalLeaderboardView, GroupLeaderboardView

urlpatterns = [
    path("group/<int:group_id>", GroupLeaderboardView.as_view(), name="group-leaderboard"),
    path("global", GlobalLeaderboardView.as_view(), name="global-leaderboard"),
]
