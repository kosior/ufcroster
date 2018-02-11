from django.apps import apps
from django.db.models import Sum, Case, When, IntegerField, Prefetch, QuerySet, Manager


def get_fight_model():
    return apps.get_model('fighters', 'Fight')


def get_fight_details_model():
    return apps.get_model('fighters', 'FightDetails')


class FighterQuerySet(QuerySet):
    def with_urls(self):
        return self.select_related('urls')

    def with_record(self):
        return self.select_related('record')

    def details(self):
        return self.select_related('record', 'urls')

    def by_country(self, country_code):
        return self.with_record().filter(
            country=country_code
        ).prefetch_related('images').only('slug', 'name', 'record__total')

    def get_by_sherdog_url(self, url):
        return self.get(urls__sherdog=url)

    def full_fighter(self):
        Fight = get_fight_model()
        FightDetails = get_fight_details_model()
        qs = Fight.objects.fight_with_relations().exclude(details__status=FightDetails.UPCOMING)
        prefetch = Prefetch('fights', queryset=qs, to_attr='fights_list')
        return self.details().prefetch_related(prefetch)


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

    def pro_record(self):
        FightDetails = get_fight_details_model()
        return self.fights.filter(details__type=FightDetails.PROFESSIONAL).aggregate(
            wins=Sum(Case(When(result=self.model.WIN, then=1), output_field=IntegerField(), default=0)),
            losses=Sum(Case(When(result=self.model.LOSS, then=1), output_field=IntegerField(), default=0)),
            draws=Sum(Case(When(result=self.model.DRAW, then=1), output_field=IntegerField(), default=0)),
            nc=Sum(Case(When(result=self.model.NOCONTEST, then=1), output_field=IntegerField(), default=0)),

            wins_ko_tko=Sum(Case(When(details__method_type=FightDetails.KO_TKO, result=self.model.WIN, then=1),
                                 output_field=IntegerField(), default=0)),
            wins_sub=Sum(Case(When(details__method_type=FightDetails.SUBMISSION, result=self.model.WIN, then=1),
                              output_field=IntegerField(), default=0)),
            wins_dec=Sum(Case(When(details__method_type=FightDetails.DECISION, result=self.model.WIN, then=1),
                              output_field=IntegerField(), default=0)),
            wins_other=Sum(Case(When(details__method_type=FightDetails.OTHER, result=self.model.WIN, then=1),
                                output_field=IntegerField(), default=0)),

            losses_ko_tko=Sum(Case(When(details__method_type=FightDetails.KO_TKO, result=self.model.LOSS, then=1),
                                   output_field=IntegerField(), default=0)),
            losses_sub=Sum(Case(When(details__method_type=FightDetails.SUBMISSION, result=self.model.LOSS, then=1),
                                output_field=IntegerField(), default=0)),
            losses_dec=Sum(Case(When(details__method_type=FightDetails.DECISION, result=self.model.LOSS, then=1),
                                output_field=IntegerField(), default=0)),
            losses_other=Sum(Case(When(details__method_type=FightDetails.OTHER, result=self.model.LOSS, then=1),
                                  output_field=IntegerField(), default=0)),

            draws_f=Sum(Case(When(details__method_type=FightDetails.DRAW, then=1), output_field=IntegerField(),
                             default=0)),

            nc_f=Sum(Case(When(details__method_type=FightDetails.NC, then=1), output_field=IntegerField(), default=0)),
        )


FighterManagerWithQueryset = FighterManager.from_queryset(FighterQuerySet)


class FightDetailsManager(Manager):
    pass


class FightManager(Manager):
    def fight_with_relations(self):
        return self.select_related(
            'opponent',
            'opponent__urls',
            'details',
            'details__event',
        )

    def full_fights(self, fighter):
        return self.fight_with_relations().filter(fighter=fighter)
