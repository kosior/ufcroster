from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from model_utils.models import TimeStampedModel

from .managers import NotificationManager


class Notification(TimeStampedModel):
    UPCOMING = 'U'
    RESULTS = 'R'

    TYPES = (
        (UPCOMING, 'Upcoming'),
        (RESULTS, 'Results')
    )

    type = models.CharField(max_length=4, choices=TYPES)
    response_id = models.CharField(max_length=128, blank=True, null=True)

    objects = NotificationManager()


class Subscription(TimeStampedModel):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=256, unique=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.email} Active: {self.is_active}'

    @property
    def action_link(self):
        if self.token:
            if not self.is_active:
                part_url = reverse('subscriptions:activate')
                return f'{settings.SITE_URL}{part_url}?token={self.token}'
            else:
                part_url = reverse('subscriptions:deactivate')
                return f'{settings.SITE_URL}{part_url}?token={self.token}'
