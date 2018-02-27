from celery.task import task

from common.utils import send_email
from fighters.models import Fight
from .models import Notification


@task
def send_upcoming_email_notification():
    notification_type = Notification.UPCOMING
    notification = Notification(type=notification_type)
    last_notification_date = Notification.objects.last_date(notification_type)
    fights = list(Fight.objects.fight_with_relations().upcoming().filter(created__gt=last_notification_date))
    if fights:
        # get user emails
        json_response = send_email('', 'Upcoming test', template_name='emails/upcoming_notify.html',
                                   context={'fights': fights})
        notification.response_id = json_response.get('id')

    notification.save()
    return notification.id


@task
def send_results_email_notification():
    notification_type = Notification.RESULTS
    notification = Notification(type=notification_type)
    last_notification_date = Notification.objects.last_date(notification_type)

    fights = list(Fight.objects.fight_with_relations().past().filter(details__modified__gt=last_notification_date))
    fights = [fight for fight in fights if fight.was_previously_upcoming]

    if fights:
        # get user emails
        json_response = send_email('', 'Results test', template_name='emails/results_notify.html',
                                   context={'fights': fights})
        notification.response_id = json_response.get('id')

    notification.save()
    return notification.id
