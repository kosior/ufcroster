from django.db import models
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
