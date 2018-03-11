import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from common.utils import send_email
from .models import Subscription
from .utils import generate_token

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Subscription)
def create_subscription(sender, instance, created, **kwargs):
    if created:
        instance.token = generate_token(instance.email, False)
        instance.save()
        send_email(instance.email, 'Activation Link', template_name='emails/activate_subscription.html',
                   context={'link': instance.action_link})
