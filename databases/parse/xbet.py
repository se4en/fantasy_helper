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

            session = HTMLSession()
            r = session.get(_url)

            # render JS
            r.html.render(retries=1, wait=0.1, timeout=20)

            game_html = r.html.find("#allBetsTable", first=True)

            # 4 - list index of block with only needed koeffs
            total_1_all = game_html.find(containing="Индивидуальный тотал 1-го")[4]
            total_1_more_1_5 = float(total_1_all.find("div", containing="1.5 Б", first=True)
                                     .find("i", first=True).text)
            total_1_less_0_5 = float(total_1_all.find("div", containing="0.5 М", first=True)
                                     .find("i", first=True).text)

            total_2_all = game_html.find(containing="Индивидуальный тотал 2-го")[4]
            total_2_more_1_5 = float(total_2_all.find("div", containing="1.5 Б", first=True)
                                     .find("i", first=True).text)
            total_2_less_0_5 = float(total_2_all.find("div", containing="0.5 М", first=True)
                                     .find("i", first=True).text)

            # here we need update table
            # we need find Team like: home_team = Leagues.find_by_name()

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
    _url = "https://1xstavka.ru/line/Football/127733-Spain-La-Liga/106480371-Celta-Atletico-Madrid/"

    """
    response = requests.get(_url)
    print(response.text)
    soup = BeautifulSoup(response.text, 'lxml')
    """


    session = HTMLSession()
    r = session.get(_url)

    r.html.render(retries=1, wait=0.1, timeout=20)


    game_html = r.html.find("#allBetsTable", first=True)



    # 4 - list index of block with only needed coefs
    total_1_all = game_html.find(containing="Индивидуальный тотал 1-го")[4]
    total_1_more_1_5 = float(total_1_all.find("div", containing="1.5 Б", first=True)
                           .find("i", first=True).text)
    total_1_less_0_5 = float(total_1_all.find("div", containing="0.5 М", first=True)
                           .find("i", first=True).text)

    total_2_all = game_html.find(containing="Индивидуальный тотал 2-го")[4]
    total_2_more_1_5 = float(total_2_all.find("div", containing="1.5 Б", first=True)
                           .find("i", first=True).text)
    total_2_less_0_5 = float(total_2_all.find("div", containing="0.5 М", first=True)
                           .find("i", first=True).text)


    print(game_html.html)

    print("AFter:")

    print(total_1_more_1_5, total_1_less_0_5, total_2_more_1_5, total_2_less_0_5)
