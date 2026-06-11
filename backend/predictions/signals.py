from django.db.models.signals import post_save
from django.dispatch import receiver

from tournaments.models import Match


@receiver(post_save, sender=Match)
def recalculate_predictions_when_match_finishes(sender, instance, **kwargs):
    if instance.status != Match.Status.FINISHED:
        return
    if instance.home_score is None or instance.away_score is None:
        return

    from predictions.services.scoring import recalculate_match_scores

    recalculate_match_scores(instance)
