from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from tournaments.services.subscriptions import subscribe_user_to_default_world_cup

User = get_user_model()


@receiver(post_save, sender=User)
def auto_subscribe_user_to_world_cup(sender, instance, created, **kwargs):
    if created and instance.is_active and not instance.is_staff:
        subscribe_user_to_default_world_cup(instance)
