from rest_framework import serializers

from .models import Match, Stage, Team, Tournament


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("id", "name", "code", "flag_url")


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ("id", "name", "order", "stage_type")


class MatchSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    winner_team = TeamSerializer(read_only=True)
    stage_name = serializers.CharField(source="stage.name", read_only=True)
    is_knockout = serializers.BooleanField(read_only=True)
    is_locked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Match
        fields = (
            "id",
            "tournament",
            "stage",
            "stage_name",
            "home_team",
            "away_team",
            "kickoff_time",
            "status",
            "home_score",
            "away_score",
            "winner_team",
            "is_knockout",
            "is_locked",
        )


class MatchResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ("home_score", "away_score", "winner_team", "status")

    def validate(self, attrs):
        instance = self.instance
        home_score = attrs.get("home_score", instance.home_score)
        away_score = attrs.get("away_score", instance.away_score)
        winner_team = attrs.get("winner_team", instance.winner_team)

        if instance.is_knockout and home_score == away_score and not winner_team:
            raise serializers.ValidationError(
                {"winner_team": "Winner is required for tied knockout matches."}
            )
        return attrs


class TournamentListSerializer(serializers.ModelSerializer):
    stage_count = serializers.IntegerField(source="stages.count", read_only=True)
    match_count = serializers.IntegerField(source="matches.count", read_only=True)

    class Meta:
        model = Tournament
        fields = (
            "id",
            "name",
            "year",
            "start_date",
            "end_date",
            "is_archived",
            "stage_count",
            "match_count",
        )


class TournamentDetailSerializer(serializers.ModelSerializer):
    stages = StageSerializer(many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = (
            "id",
            "name",
            "year",
            "start_date",
            "end_date",
            "is_archived",
            "stages",
        )


class TournamentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tournament
        fields = ("name", "year", "start_date", "end_date", "is_archived")


class StageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ("tournament", "name", "order", "stage_type")


class TeamCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ("name", "code", "flag_url")


class MatchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = (
            "tournament",
            "stage",
            "home_team",
            "away_team",
            "kickoff_time",
            "status",
        )
