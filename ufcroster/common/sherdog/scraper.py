import logging

import requests
from bs4 import BeautifulSoup

from .base import SherdogException
from .decorators import disallow_none_return
from .fighter import FullFighter
from .fights import Fights
from .upcoming import UpcomingFight

logger = logging.getLogger(__name__)


def get_html_content(url, timeout=2, exception_cls=SherdogException):
    logger.info(f'Getting {url}')
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise exception_cls('Request timeout.')
    except requests.exceptions.HTTPError:
        raise exception_cls('Bad request.')
    else:
        return response.content


class SherdogScraper:
    _content = None
    helpers = {'fighter': FullFighter, 'upcoming': UpcomingFight, 'fights': Fights}

    def __init__(self, url_):
        self.url_ = url_

    def get_html_content(self, timeout=2):
        logger.info(f'Getting {self.url_}')
        try:
            response = requests.get(self.url_, timeout=timeout)
            response.raise_for_status()
        except (requests.exceptions.Timeout, requests.exceptions.HTTPError):
            raise SherdogException('Error getting html content.')
        else:
            return response.content

    @disallow_none_return
    def _get_soup_content(self):
        soup = BeautifulSoup(self.get_html_content(), 'html.parser')
        return soup.find('section').find_previous(class_='col_left')

    @property
    def content(self):
        if self._content is None:
            self._content = self._get_soup_content()
        return self._content

    def _get_helper_instance(self, helper_key):
        helper_cls = self.helpers[helper_key]
        return helper_cls(self.url_, self.content)

    def _get_result(self, helper_key, **kwargs):
        try:
            return self._get_helper_instance(helper_key).get(**kwargs)
        except (ValueError, SherdogException):
            logger.exception('Sherdog Error')
            return

    def fighter(self):
        return self._get_result('fighter')

    def upcoming(self):
        return self._get_result('upcoming')

    def fights(self, pro_fights_num_in_db=0):
        return self._get_result('fights', pro_fights_num_in_db=pro_fights_num_in_db)

    def fight(self, ordinal):
        return self._get_helper_instance('fights').get_by_ordinal(ordinal)

    def pro_fights_count(self):
        return self._get_helper_instance('fights').get_pro_fights_count()
