import sys, os
import requests
import json
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from db.parse.sports import Sports
from db.database import Session
from db.models.coeff import Coeff


class XBet:

    def __init__(self, leagues: dict = None):
        self.sports = Sports()

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

    def __update_match(self, league_name: str, match_info: dict,
                       cur_tour: bool = False, new_round: bool = True) -> bool:
        try:
            home_team = match_info['homeTeam']['name']
            away_team = match_info['awayTeam']['name']
            match_url = match_info['url']

            print(f"Update match {home_team} vs {away_team}")

            # not match
            if "голы" in home_team or "специальное" in home_team or "Хозяева" in home_team:
                return False

            html_session = HTMLSession()
            r = html_session.get(match_url)

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

            # update db
            db_session: SQLSession = Session()
            if new_round:
                home_coeff = Coeff(
                    home_team, away_team, league_name,
                    total_1_more_1_5, total_2_less_0_5, True, cur_tour
                )
                away_coeff = Coeff(
                    away_team, home_team, league_name,
                    total_2_more_1_5, total_1_less_0_5, False, cur_tour
                )
                db_session.add_all([home_coeff, away_coeff])
                db_session.commit()
                return True
            # update home team
            db_session.query(Coeff).filter(and_(
                Coeff.team == home_team,
                Coeff.team_against == away_team,
                Coeff.league == league_name
            )).update({
                Coeff.more_1_5: total_1_more_1_5,
                Coeff.clean_sheet: total_2_less_0_5
            })
            # update away team
            db_session.query(Coeff).filter(and_(
                Coeff.team == away_team,
                Coeff.team_against == home_team,
                Coeff.league == league_name
            )).update({
                Coeff.more_1_5: total_2_more_1_5,
                Coeff.clean_sheet: total_1_less_0_5
            })
            db_session.commit()
            return True
        except Exception as ex:
            # logs here
            print(ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return False

    def update_league(self, league_name: str, new_round: bool) -> bool:

        if league_name not in self._leagues:
            return False

        try:
            response = requests.get(self._leagues[league_name])
            soup = BeautifulSoup(response.text, 'lxml')

            all_matches = json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents))

            if len(all_matches) == 0:
                return False

            cur_round_matches = self.sports.get_games_count(league_name)
            updated_matches = 0
            checked_matches = 0
            # update cur round
            while updated_matches < cur_round_matches:
                if self.__update_match(league_name, all_matches[checked_matches],
                                       True, new_round):
                    updated_matches += 1
                checked_matches += 1
            # update next round
            while checked_matches < len(all_matches):
                self.__update_match(league_name, all_matches[checked_matches],
                                    False, new_round)
                checked_matches += 1

            return True
        except Exception as ex:
            # logs here
            print(ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return False

    def update_all(self) -> bool:

        return all(list(map(lambda x: self.update_league(x), self._leagues)))


if __name__ == "__main__":
    xbet = XBet()
    xbet.update_league("Russia", new_round=True)
    # #_1x = XBet()
    # #_1x.update_all()
    # _url = "https://1xstavka.ru/line/Football/127733-Spain-La-Liga/106480371-Celta-Atletico-Madrid/"
    #
    # """
    # response = requests.get(_url)
    # print(response.text)
    # soup = BeautifulSoup(response.text, 'lxml')
    # """
    #
    #
    # session = HTMLSession()
    # r = session.get(_url)
    #
    # r.html.render(retries=1, wait=0.1, timeout=20)
    #
    #
    # game_html = r.html.find("#allBetsTable", first=True)
    #
    #
    #
    # # 4 - list index of block with only needed coefs
    # total_1_all = game_html.find(containing="Индивидуальный тотал 1-го")[4]
    # total_1_more_1_5 = float(total_1_all.find("div", containing="1.5 Б", first=True)
    #                        .find("i", first=True).text)
    # total_1_less_0_5 = float(total_1_all.find("div", containing="0.5 М", first=True)
    #                        .find("i", first=True).text)
    #
    # total_2_all = game_html.find(containing="Индивидуальный тотал 2-го")[4]
    # total_2_more_1_5 = float(total_2_all.find("div", containing="1.5 Б", first=True)
    #                        .find("i", first=True).text)
    # total_2_less_0_5 = float(total_2_all.find("div", containing="0.5 М", first=True)
    #                        .find("i", first=True).text)
    #
    #
    # print(game_html.html)
    #
    # print("AFter:")
    #
    # print(total_1_more_1_5, total_1_less_0_5, total_2_more_1_5, total_2_less_0_5)
