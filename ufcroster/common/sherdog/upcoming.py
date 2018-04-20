from .base import BaseSherdog, build_url


class UpcomingFightHelper:
    def __init__(self, soup_content, ordinal, fighter_url):
        self.fight_content = soup_content
        self.ordinal = ordinal
        self.fighter_url = fighter_url

    def get_event_title(self):
        return self.fight_content.find(itemprop='name').text

    def get_start_date(self):
        return self.fight_content.find(itemprop='startDate')['content']

    def get_location(self):
        return self.fight_content.find(itemprop='location').text

    def get_opponent(self):
        result = self.fight_content.find(class_='fighter right_side')
        url = build_url(result.find('a')['href'])
        name = result.find(itemprop='name').text
        return name, url

    def get_event_url(self):
        return build_url(self.fight_content.find(class_='single_button')['href'])

    def get(self):
        opponent_name, opponent_url = self.get_opponent()

        return {
            'ordinal': self.ordinal,
            'result': '',
            'opponent': {
                'name': opponent_name,
                'urls': {
                    'sherdog': opponent_url,
                },
            },
            'details': {
                'date': self.get_start_date(),
                'type': 'P',
                'status': 'U',
                'method': '',
                'round': '',
                'time': '',
                'referee': '',
                'event': {
                    'sherdog_url': self.get_event_url(),
                    'title': self.get_event_title(),
                    'date': self.get_start_date(),
                    'location': self.get_location(),
                }
            },
        }


class UpcomingFight(BaseSherdog):
    def _get_content_soup(self):
        return self.html_content.find(class_='event-upcoming')

    def get_ordinal(self):
        fights_content = self.content_soup.find_all(class_='module fight_history')
        for content in fights_content:
            if content.h2.text == 'Fight History - Pro':
                return len(content.find_all('tr'))
        return 1

    def _get(self):
        if self.content_soup:
            return UpcomingFightHelper(self.content_soup, ordinal=self.get_ordinal(), fighter_url=self.url).get()
