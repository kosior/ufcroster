from django.apps import apps
from django.db.models import Prefetch, QuerySet, Manager


def get_fight_model():
    return apps.get_model('fighters', 'Fight')


def get_fight_details_model():
    return apps.get_model('fighters', 'FightDetails')


class FighterQuerySet(QuerySet):
    def details(self):
        return self.select_related('record', 'urls')

    def full_fighter(self):
        Fight = get_fight_model()
        qs = Fight.objects.fight_with_relations()
        prefetch = Prefetch('fights', queryset=qs, to_attr='fights_list')
        return self.details().prefetch_related(prefetch)

    def by_country(self, country_code):
        return self.select_related('record').filter(country=country_code).only('slug', 'name', 'record__total', 'image')

    def active(self):
        return self.filter(in_ufc=True, active=True)


class FighterManager(Manager):
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


class FightDetailsManager(Manager):
    def rest_get_or_create(self, fighter, **kwargs):
        try:
            details = self.get(**kwargs)
        except self.model.DoesNotExist:
            return self.create(**kwargs), True
        else:
            if details.fights.filter(opponent=fighter).exists():
                return details, False
            return self.create(**kwargs), True


class FightQuerySet(QuerySet):
    def fight_with_relations(self):
        return self.select_related(
            'fighter',
            'fighter__urls',
            'fighter__record',
            'opponent',
            'opponent__urls',
            'details',
            'details__event',
        )

    def upcoming(self):
        return self.filter(details__status='U')

    def full_fights(self, fighter):
        return self.fight_with_relations().filter(fighter=fighter)

    def upcoming_by_country(self, country_code):
        return self.fight_with_relations().upcoming().filter(fighter__country=country_code)
