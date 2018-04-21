import copy
import logging
from datetime import datetime

from .base import BaseSherdog, SherdogException, build_url
from .upcoming import UpcomingFightHelper


logger = logging.getLogger(__name__)


class FightHelper:
    def __init__(self, soup_content, ordinal, fight_type, fighter_url):
        self.soup = soup_content.find_all('td')
        self.ordinal = ordinal
        self.fight_type = fight_type
        self.fighter_url = fighter_url

    def get_result(self):
        results = {'win': 'W', 'loss': 'L', 'draw': 'D', 'N/C': 'NC', 'NC': 'NC'}
        result = self.soup[0].text
        return results.get(result)

    def get_opponent_name(self):
        return self.soup[1].text

    def get_opponent_url(self):
        return build_url(self.soup[1].find('a')['href'])

    def get_event_url(self):
        return build_url(self.soup[2].find('a')['href'])

    def get_event_title_and_date(self):
        result = self.soup[2]
        date = result.find(class_='sub_line').text
        date = str(datetime.strptime(date, '%b / %d / %Y'))
        event_title = result.a.text
        return event_title, date

    def get_method_and_referee(self):
        result = copy.copy(self.soup[3])
        referee = result.span.extract().text
        method = result.text
        return method, referee

    def get_round(self):
        return self.soup[4].text

    def get_time(self):
        return self.soup[5].text

    def qualify_method_helper(self, method):
        methods_map = {
            'KO/TKO': ['ko', 'tko'],
            'SUBMISSION': ['submission', 'technical submission'],
            'DECISION': ['decision'],
            'OTHER': ['dq', 'disqualification', 'n/a'],
            'NC': ['nc', 'no decision', 'no contest'],
            'DRAW': ['draw']
        }

        method = method.lower()

        for key, start_values in methods_map.items():
            for start_value in start_values:
                if method.startswith(start_value):
                    return key

        logger.warning(f'None fight method. {self.fighter_url}')
        return None

    def get(self):
        method, referee = self.get_method_and_referee()
        event_title, date = self.get_event_title_and_date()
        return {
            'ordinal': self.ordinal,
            'result': self.get_result(),
            'opponent': {
                'name': self.get_opponent_name(),
                'urls': {
                    'sherdog': self.get_opponent_url(),
                },
            },
            'details': {
                'date': date,
                'type': self.fight_type,
                'status': 'P',
                'method': method,
                'method_type': self.qualify_method_helper(method),
                'round': self.get_round(),
                'time': self.get_time(),
                'referee': referee,
                'event': {
                    'sherdog_url': self.get_event_url(),
                    'title': event_title,
                    'date': date,
                }
            },
        }


class Fights(BaseSherdog):
    _fights_content = None
    types = {
        'Fight History - Amateur': 'A',
        'Fight History - Pro Exhibition': 'E',
        'Fight History - Pro': 'P',
        'Upcoming Fights': 'U'
    }
    _grouped = None

    def _get_content_soup(self):
        return self.html_content.find_all(class_='module fight_history')

    def _group_content_by_type(self):
        grouped = {}
        for content in self.content_soup:
            fights_type = self.types.get(content.h2.text)

            if not fights_type:
                raise SherdogException('Could not associate fights type.')

            content = content.find_all('tr')[:0:-1]  # reverse and without first element
            grouped[fights_type] = content
        return grouped

    @property
    def grouped(self):
        if self._grouped is None:
            self._grouped = self._group_content_by_type()
        return self._grouped

    def get_fights_count(self):
        return {key: len(value) for key, value in self.grouped.items()}

    def get_pro_fights_count(self):
        return len(self.grouped.get('P', ''))

    def _get_single_type(self, content, fights_type=None, skip_first=0):
        fights = []

        if fights_type == 'U':
            pass
            # ordinal = self.get_pro_fights_count() + 1
            # fights.append(UpcomingFightHelper(content[0], ordinal=ordinal, fighter_url=self.url).get())
        else:
            content = content[skip_first:]
            start = skip_first + 1
            for ordinal, raw_fight in enumerate(content, start=start):
                fight = FightHelper(raw_fight, ordinal, fight_type=fights_type, fighter_url=self.url)
                fights.append(fight.get())
        return fights

    def _get(self, pro_fights_num_in_db=0):
        full_fight_list = []

        if pro_fights_num_in_db:
            fights_type = 'P'
            content = self.grouped[fights_type]
            full_fight_list.extend(self._get_single_type(content, fights_type, skip_first=pro_fights_num_in_db))
        else:
            for fights_type, content in self.grouped.items():
                full_fight_list.extend(self._get_single_type(content, fights_type))
        return full_fight_list

    def get_by_ordinal(self, ordinal, fight_type='P'):
        raw_fights = self.grouped.get(fight_type)
        raw_fight = raw_fights[ordinal - 1]  # possible key error
        return FightHelper(raw_fight, ordinal, fight_type=fight_type, fighter_url=self.url).get()
