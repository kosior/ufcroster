from django.core.management.base import BaseCommand

from ...utils import create_or_update_fighter, update_fighter_fights


class Command(BaseCommand):
    help = 'Adding new fighter to db'

    def add_arguments(self, parser):
        parser.add_argument('sherdog_url', type=str)
        parser.add_argument(
            '--in_ufc',
            action='store_true',
            dest='in_ufc',
            help='Flag if fighter in UFC',
        )

    def handle(self, *args, **options):
        sherdog_url = options['sherdog_url']
        in_ufc = options['in_ufc']
        fighter = create_or_update_fighter(sherdog_url, in_ufc=in_ufc, active=True)
        update_fighter_fights(fighter)
