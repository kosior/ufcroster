from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    venue = models.CharField(max_length=255, blank=True)
    poster = models.ImageField(blank=True)
    promotion = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
