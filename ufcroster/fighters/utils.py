import logging

from django.db.models import Sum, Case, When, IntegerField
from django.db.utils import IntegrityError

from common.sherdog.scraper import SherdogScraper
from .api.serializers import FightSerializer, FighterSerializer
from .models import Fighter, Fight, FightDetails

logger = logging.getLogger(__name__)


def create_or_update_fighter(sherdog_url, in_ufc=False, active=False):
    scraper = SherdogScraper(sherdog_url)

    fighter_data = scraper.fighter()
    fighter_data.update({'in_ufc': in_ufc, 'active': active})

    instance_kwarg = {}
    instance = Fighter.objects.filter(urls__sherdog=sherdog_url).first()
    if instance:
        instance_kwarg['instance'] = instance

    fighter = FighterSerializer(data=fighter_data, **instance_kwarg)
    if fighter.is_valid():
        fighter = fighter.save()

        fights_data = scraper.fights(pro_fights_num_in_db=fighter.pro_fights_count())
        for fight_d in fights_data:
            fight = FightSerializer(data=fight_d, context={'slug': fighter.slug})
            if fight.is_valid():
                try:
                    fight.save()
                except IntegrityError:
                    logger.error(f'Error when saving fight ({fighter.slug})')
            else:
                logger.warning(f'Invalid fight data ({fighter.slug})')
    else:
        logger.warning(f'Invalid fighter data {sherdog_url}')

    return fighter


def set_opponent_info(fight):
    details = fight.details
    opponent = fight.opponent
    opponent_fight_ordinal = opponent.get_fight_ordinal(fight_details=details)

    if not opponent_fight_ordinal:
        opponent_sherdog_url = opponent.urls.sherdog
        sherdog = SherdogScraper(opponent_sherdog_url)
        context = {'slug': opponent.slug}

        for fight_data in sherdog.fights(pro_fights_num_in_db=opponent.pro_fights_count()):
            fight_serialized = FightSerializer(data=fight_data, context=context)
            if fight_serialized.is_valid():
                try:
                    fight_serialized.save()
                except IntegrityError:
                    logger.error(f'Error when saving fight ({opponent.slug})')

        opponent_fight_ordinal = opponent.get_fight_ordinal(fight_details=details)

    if not opponent_fight_ordinal:
        logger.error(f'Error setting opponent info')
        return

    opponent_record_before = opponent.fights.filter(
        ordinal__lt=opponent_fight_ordinal, details__type=details.type
    ).aggregate(
        wins=Sum(Case(When(result=Fight.WIN, then=1), output_field=IntegerField(), default=0)),
        losses=Sum(Case(When(result=Fight.LOSS, then=1), output_field=IntegerField(), default=0)),
        draws=Sum(Case(When(result=Fight.DRAW, then=1), output_field=IntegerField(), default=0)),
        nc=Sum(Case(When(result=Fight.NOCONTEST, then=1), output_field=IntegerField(), default=0))
    )

    min_ordinal = max(1, opponent_fight_ordinal - 5)
    ordinal_range = range(min_ordinal, opponent_fight_ordinal)

    opponent_last_5 = opponent.fights.filter(
        ordinal__in=ordinal_range, details__type=details.type
    ).values_list('result', flat=True)

    fight.opponent_last_5 = ','.join(opponent_last_5)
    fight.opponent_record_before = dict_record_to_str(opponent_record_before)

    return fight.save()


def dict_record_to_str(record_dict):
    wins = record_dict.get('wins') or 0
    losses = record_dict.get('losses') or 0
    draws = record_dict.get('draws') or 0
    nc = record_dict.get('nc') or 0

    record = f'{wins} - {losses} - {draws}'
    if nc:
        record = f'{record} N/C: {nc} '
    return record


def update_fighter_fights(fighter):
    fights = fighter.fights.filter(details__type='P').select_related('details', 'opponent')
    for fight in fights:
        set_opponent_info(fight)


def update_upcoming_fight(upcoming_fight):
    assert upcoming_fight.details.status == FightDetails.UPCOMING
    sherdog_url = upcoming_fight.fighter.urls.sherdog
    scraper = SherdogScraper(sherdog_url)
    fight_data = scraper.fight(ordinal=upcoming_fight.ordinal)
    fight = FightSerializer(instance=upcoming_fight, data=fight_data)
    if fight.is_valid():
        return fight.save()
