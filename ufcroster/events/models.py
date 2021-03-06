from django.db import models

from common.models import TimeStampedModel


class Event(TimeStampedModel):
    title = models.CharField(max_length=255)
    date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    venue = models.CharField(max_length=255, blank=True)
    poster = models.ImageField(blank=True)
    promotion = models.CharField(max_length=255, blank=True)
    sherdog_url = models.URLField(max_length=255, blank=True, null=True)
    ufc_url = models.URLField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.title
