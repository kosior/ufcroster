import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Fight, FighterRecord
from .utils import invalidate_fights_cache

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Fight)
def save_fight(sender, instance, **kwargs):
    invalidate_fights_cache([instance.fighter_id, instance.opponent_id])


@receiver(post_save, sender=FighterRecord)
def save_fight_record(sender, instance, **kwargs):
    invalidate_fights_cache([instance.fighter_id])
