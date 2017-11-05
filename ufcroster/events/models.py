from django.db import models


class Event(models.Model):
    title = models.CharField(max_length=255, unique=True)
    date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    venue = models.CharField(max_length=255, blank=True)
    poster = models.ImageField(blank=True)
    promotion = models.CharField(max_length=255, blank=True)
    sherdog_url = models.URLField(max_length=255, blank=True, null=True, unique=True)
    ufc_url = models.URLField(max_length=255, blank=True, null=True, unique=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.title
