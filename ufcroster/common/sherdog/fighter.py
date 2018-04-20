from .base import BaseSherdog
from .decorators import disallow_none_return, ignore_attr_err


class FighterInfo(BaseSherdog):
    def _get_content_soup(self):
        return self.html_content.find(class_='module bio_fighter vcard')

    @disallow_none_return
    def get_name(self):
        return self.content_soup.find(class_='fn').text

    @ignore_attr_err
    def get_nickname(self):
        return self.content_soup.find(class_='nickname').text.strip('"')

    def get_birthdate(self):
        birthdate = self.content_soup.find(itemprop='birthDate').text
        if birthdate == 'N/A':
            return None
        return birthdate

    def get_birthplace(self):
        return self.content_soup.find(itemprop='address').text

    def get_country_code(self):
        src = self.content_soup.find(class_='big_flag').get('src')
        return src.split('/')[-1].split('.')[0].upper()

    def get_country(self):
        return self.content_soup.find(itemprop='nationality').text

    def get_height(self):
        height = self.content_soup.find(class_='height').get_text(' ', strip=True).split(' ')
        height_imp = height[1]
        height_met = height[2]
        return height_met, height_imp

    def get_weight(self):
        weight = self.content_soup.find(class_='weight').get_text(' ', strip=True).split(' ')
        weight_imp = weight[1]
        weight_met = weight[3]
        return weight_met, weight_imp

    def get_team(self):
        return self.content_soup.find(itemprop='memberOf').text

    def get_weight_class(self):
        return self.content_soup.find(class_='title').text

    def _get(self):
        height_met, height_imp = self.get_height()
        weight_met, weight_imp = self.get_weight()

        return {
            'name': self.get_name(),
            'nickname': self.get_nickname(),
            'birthdate': self.get_birthdate(),
            'birthplace': self.get_birthplace(),
            'country': self.get_country_code(),
            'height': height_met,
            'height_imp': height_imp,
            'weight': weight_met,
            'weight_imp': weight_imp,
            'weight_class': self.get_weight_class(),
            'team': self.get_team(),
        }


class FighterRecord(BaseSherdog):
    _methods = ['KO/TKO', 'SUBMISSIONS', 'DECISIONS', 'OTHERS']

    def _get_content_soup(self):
        return self.html_content.find(class_='record')

    def get_wins(self):
        return int(self.content_soup.find(class_='bio_graph').find(class_='counter').text)

    def get_wins_all(self):
        results = self.content_soup.find(class_='bio_graph').find_all(class_='graph_tag')
        results = [r.get_text(' ', strip=True).split(' ') for r in results]
        results = {r[1]: int(r[0]) for r in results} or {}
        return (results.get(method, 0) for method in self._methods)

    def get_losses(self):
        return int(self.content_soup.find(class_='bio_graph loser').find(class_='counter').text)

    def get_losses_all(self):
        results = self.content_soup.find(class_='bio_graph loser').find_all(class_='graph_tag')
        results = [r.get_text(' ', strip=True).split(' ') for r in results]
        results = {r[1]: int(r[0]) for r in results} or {}
        return (results.get(method, 0) for method in self._methods)

    @ignore_attr_err(default=(0, 0))
    def get_draws_and_nc(self):
        results = self.content_soup.find(class_='right_side').find_all(class_='card')
        results = [r.get_text(' ', strip=True).split(' ') for r in results]
        results = {r[0]: r[1] for r in results} or {}
        return results.get('Draws', 0), results.get('N/C', 0)

    def _get(self):
        wins = self.get_wins()
        losses = self.get_losses()
        wins_ko_tko, wins_sub, wins_dec, wins_other = self.get_wins_all()
        losses_ko_tko, losses_sub, losses_dec, losses_other = self.get_losses_all()
        draws, nc = self.get_draws_and_nc()
        return {
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'nc': nc,
            'wins_ko_tko': wins_ko_tko,
            'wins_sub': wins_sub,
            'wins_dec': wins_dec,
            'wins_other': wins_other,
            'losses_ko_tko': losses_ko_tko,
            'losses_sub': losses_sub,
            'losses_dec': losses_dec,
            'losses_other': losses_other,
        }


class FullFighter:
    def __init__(self, url, content):
        self.url = url
        self.fighter_info = FighterInfo(url, content)
        self.fighter_record = FighterRecord(url, content)

    def get(self):
        full_fighter = {'urls': {'sherdog': self.url, }}
        full_fighter.update(self.fighter_info.get())
        full_fighter.update({'record': self.fighter_record.get()})
        return full_fighter
