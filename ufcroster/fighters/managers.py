from django.apps import apps
from django.db import models


def get_fight_model():
    return apps.get_model('fighters', 'Fight')


class FighterQuerySet(models.QuerySet):
    def with_urls(self):
        return self.select_related('urls')

    def with_record(self):
        return self.select_related('record')

    def details(self):
        return self.select_related('record', 'urls')

    def get_by_sherdog_url(self, url):
        return self.get(urls__sherdog=url)

    def full_fighter(self):
        Fight = get_fight_model()
        qs = Fight.objects.fight_with_relations()
        prefetch = models.Prefetch('fights', queryset=qs, to_attr='fights_list')
        return self.details().prefetch_related(prefetch)


class FighterManager(models.Manager):
    def create_full(self, **kwargs):
        urls_kw = kwargs.pop('urls', {})
        record_kw = kwargs.pop('record', {})
        fighter = self.create(**kwargs)
        fighter.create_urls(**urls_kw)
        fighter.create_record(**record_kw)
        return fighter

    def rest_get_or_create(self, **kwargs):
        name = kwargs.get('name')
        sherdog_url = kwargs.get('urls').get('sherdog')
        try:
            return self.get(name=name, urls__sherdog=sherdog_url), False
        except self.model.DoesNotExist:
            return self.create_full(**kwargs), True


FighterManagerWithQueryset = FighterManager.from_queryset(FighterQuerySet)


class FightDetailsManager(models.Manager):
    pass


class FightManager(models.Manager):
    def fight_with_relations(self):
        return self.select_related(
            'opponent',
            'opponent__urls',
            'details',
            'details__event',
        )

    def full_fights(self, fighter):
        return self.fight_with_relations().filter(fighter=fighter)
