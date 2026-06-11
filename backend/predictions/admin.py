from django.contrib import admin

from .models import Prediction


@admin.register(Prediction)
class PredictionAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "group",
        "match",
        "predicted_home_score",
        "predicted_away_score",
        "points_awarded",
    )
    list_filter = ("group", "match__tournament")
    raw_id_fields = ("user", "group", "match", "predicted_winner_team")
