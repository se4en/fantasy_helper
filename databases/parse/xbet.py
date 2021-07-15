import requests
import json
from bs4 import BeautifulSoup
from requests_html import HTMLSession


class XBet:

    def __init__(self, leagues: dict = None):
        if leagues:
            self._leagues = leagues
            return

        self._leagues = {
            'Russia': 'https://1xstavka.ru/line/Football/225733-Russia-Premier-League/',
            'England': 'https://1xstavka.ru/line/Football/88637-England-Premier-League/',
            'France': 'https://1xstavka.ru/line/Football/12821-France-Ligue-1/',
            'Germany': 'https://1xstavka.ru/line/Football/96463-Germany-Bundesliga/',
            'Spain': 'https://1xstavka.ru/line/Football/127733-Spain-La-Liga/',
            'Netherlands': 'https://1xstavka.ru/line/Football/2018750-Netherlands-Eredivisie/',
            'Championship': 'https://1xstavka.ru/line/Football/105759-England-Championship/',
            'Turkey': 'https://www.fonbet.ru/bets/football/12973/',
            'Italy': 'https://www.fonbet.ru/bets/football/11924/',
            'Portugal': 'https://www.fonbet.ru/bets/football/11939',
            'UEFA_1': 'https://www.fonbet.ru/bets/football/15290',
            'UEFA_2': 'https://www.fonbet.ru/bets/football/15290',
        }

    def _update_match(self, league_name: str, match_info: dict) -> bool:

        try:
            home_team = match_info['homeTeam']['name']
            away_team = match_info['awayTeam']['name']
            match_url = match_info['url']

            if "голы" in home_team or "специальное" in home_team:  # not match
                return True

            response = requests.get(match_url)
            print(response.text)
            soup = BeautifulSoup(response.text, 'lxml')

            away_koeff_down = float(soup.find_all("span", string="Индивидуальный тотал 1 Меньше 0.5")[0]. \
                parent.find("span", {"class": "koeff"}).text)
            print("result:")
            print(away_koeff_down)

            print(home_team, away_team, match_url)
        except Exception as ex:
            # logs here
            print(ex)
            return False
        else:
            return True

    def update_league(self, league_name: str) -> bool:

        if league_name not in self._leagues:
            return False

        try:
            response = requests.get(self._leagues[league_name])
            soup = BeautifulSoup(response.text, 'lxml')

            all_matches = json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents))

            # здесь надо получать матчи в туре, чтобы отмечать в бд, относится ли матч к текуущему туру


            return all(list(map(lambda x: self._update_match(league_name, x), all_matches)))
        except:
            # logs here
            print("Caught it!")
            return False

    def update_all(self) -> bool:

        return all(list(map(lambda x: self.update_league(x), self._leagues)))


if __name__ == "__main__":

    #_1x = XBet()
    #_1x.update_all()
    _url = "https://1xstavka.ru/line/Football/225733-Russia-Premier-League/106034824-Rostov-Dynamo-Moscow/"

    """
    response = requests.get(_url)
    print(response.text)
    soup = BeautifulSoup(response.text, 'lxml')
    """


    session = HTMLSession()
    r = session.get(_url)

    r.html.render()


    print(r.html.find("#allBetsTable", first=True).html)