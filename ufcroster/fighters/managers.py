from django.apps import apps
from django.db import models


def get_part_fight_model():
    return apps.get_model('fighters', 'PartFight')


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
        PartFight = get_part_fight_model()
        qs = PartFight.objects.fights_with_relations()
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


class FullFightManager(models.Manager):
    def rest_create_or_update(self, **kwargs):
        event = kwargs.pop('event')
        part_fight = kwargs.pop('part_fight')
        date = part_fight.date
        opponent = part_fight.opponent
        fighter = part_fight.fighter

        q1 = models.Q(part_1__date=date, part_1__fighter=opponent, part_1__opponent=fighter)
        q2 = models.Q(part_2__date=date, part_2__fighter=opponent, part_2__opponent=fighter)

        try:
            full_fight = self.get(models.Q(event=event), q1 | q2)
        except self.model.DoesNotExist:
            return self.create(event=event, part_1=part_fight, **kwargs), True
        else:
            full_fight.fill_empty_part(part_fight)
            full_fight.save()
            return full_fight, False


class PartFightManager(models.Manager):
    def fights_with_relations(self):
        return self.select_related(
            'opponent',
            'opponent__urls',
            'details_1',
            'details_1__event',
            'details_2',
            'details_2__event',
        )

    def full_fights(self, fighter):
        return self.fights_with_relations().filter(fighter=fighter)
