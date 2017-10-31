from django.db import models


class FighterQuerySet(models.QuerySet):
    def with_urls(self):
        return self.select_related('urls')

    def with_record(self):
        return self.select_related('record')

    def details(self):
        return self.select_related('record', 'urls')
