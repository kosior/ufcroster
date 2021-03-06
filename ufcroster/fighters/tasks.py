from celery import chord
from celery.task import task
from celery.utils.log import get_task_logger
from django.utils.timezone import now

from common.sherdog.scraper import SherdogScraper
from fighters.api.serializers import FightSerializer
from subscriptions.tasks import send_upcoming_email_notification, send_results_email_notification
from .models import Fight, Fighter
from .utils import update_upcoming_fight, set_opponent_info

logger = get_task_logger(__name__)


@task
def set_opponent_info_task(fight_id):
    fight = Fight.objects.get(id=fight_id)
    set_opponent_info(fight)


@task
def check_fighter_for_upcoming(slug, sherdog_url):
    sherdog = SherdogScraper(sherdog_url)
    upcoming_data = sherdog.upcoming()
    if upcoming_data:
        upcoming = FightSerializer(data=upcoming_data, context={'slug': slug})
        if upcoming.is_valid():
            fight = upcoming.save()
            fight.fighter.record.save()
            set_opponent_info_task.delay(fight.id)
            return fight.id


@task
def update_upcoming_fight_task(upcoming_fight):
    fight = update_upcoming_fight(upcoming_fight)
    if fight:
        return fight.id


@task
def search_for_upcoming():
    fighters_with_upcoming = Fight.objects.upcoming().values_list('fighter_id', flat=True)
    fighters_data = Fighter.objects.active().exclude(id__in=fighters_with_upcoming).values_list('slug',
                                                                                                'urls__sherdog')
    tasks = [
        check_fighter_for_upcoming.signature((slug, sherdog_url), countdown=2)
        for slug, sherdog_url in fighters_data
    ]
    callback = send_upcoming_email_notification.si().on_error(send_upcoming_email_notification.si())
    chord(tasks)(callback)


@task
def update_past_upcoming():
    past_upcoming_fights = Fight.objects.fight_with_relations().upcoming().filter(details__date__lt=now())
    tasks = [update_upcoming_fight_task.s(upcoming_fight) for upcoming_fight in past_upcoming_fights]
    callback = send_results_email_notification.si().on_error(send_results_email_notification.si())
    chord(tasks)(callback)
