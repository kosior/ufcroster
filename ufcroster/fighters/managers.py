from django.db import models


class FighterQuerySet(models.QuerySet):
    def with_urls(self):
        return self.select_related('urls')
