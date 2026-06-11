from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdminMatchViewSet,
    AdminTournamentViewSet,
    MatchViewSet,
    StageViewSet,
    TeamViewSet,
    TournamentViewSet,
)

router = DefaultRouter()
router.register("", TournamentViewSet, basename="tournament")
router.register("teams", TeamViewSet, basename="team")
router.register("matches", MatchViewSet, basename="match")

admin_router = DefaultRouter()
admin_router.register("tournaments", AdminTournamentViewSet, basename="admin-tournament")
admin_router.register("stages", StageViewSet, basename="admin-stage")
admin_router.register("matches", AdminMatchViewSet, basename="admin-match")

urlpatterns = [
    path("", include(router.urls)),
    path("admin/", include(admin_router.urls)),
]
