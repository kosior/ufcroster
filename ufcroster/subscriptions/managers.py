from django.db import models
from django.utils import timezone


class NotificationManager(models.Manager):
    def last_date(self, notification_type):
        last_notification_date = self.filter(
            type=notification_type
        ).order_by('-created').values_list('created', flat=True).first()

        return last_notification_date or timezone.now() - timezone.timedelta(days=7)


