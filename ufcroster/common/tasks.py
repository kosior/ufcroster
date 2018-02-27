from celery.task import task

from .utils import send_email


@task
def send_email_task(to, subject, text='', template_name=None, context=None):
    return send_email(to, subject, text, template_name, context)
