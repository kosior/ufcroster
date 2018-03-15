import json

from django.db import models
from django.utils import timezone


class NotificationManager(models.Manager):
    def last_date(self, notification_type):
        last_notification_date = self.filter(
            type=notification_type
        ).order_by('-created').values_list('created', flat=True).first()

        return last_notification_date or timezone.now() - timezone.timedelta(days=7)


class SubscriptionsManager(models.Manager):
    def get_mailing_data(self):
        subscriptions = {s.email: s.unsubscribe_dict for s in self.filter(is_active=True)}
        emails = list(subscriptions.keys())
        recipient_vars = json.dumps(subscriptions)
        return emails, recipient_vars
