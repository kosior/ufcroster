import logging


logger = logging.getLogger(__name__)


class SherdogException(Exception):
    pass


def build_url(url):
    if url:
        return f'http://www.sherdog.com{url}'
    raise ValueError('Wrong url.')


class BaseSherdog:
    _content_soup = None

    def __init__(self, url, html_content):
        self.url = url
        self.html_content = html_content

    def _get_content_soup(self):
        # example: return self.html_content.find(class_='some-class')
        raise NotImplementedError

    @property
    def content_soup(self):
        if self._content_soup is None:
            self._content_soup = self._get_content_soup()
            # if self._content_soup is None:
            #     raise ValueError('Content is None')
        return self._content_soup

    def _get(self, **kwargs):
        raise NotImplementedError

    def get(self, **kwargs):
        try:
            return self._get(**kwargs)
        except (AttributeError, TypeError, IndexError, ValueError, KeyError, SherdogException):
            logger.exception('Sherdog Error')
            return
