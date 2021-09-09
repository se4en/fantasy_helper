import logging
import sys, os
from time import sleep

import requests
import json
from bs4 import BeautifulSoup
from requests_html import HTMLSession, AsyncHTMLSession
from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from db.parse.sports import Sports
from db.database import Session
from db.models.coeff import Coeff


class XBet:

    def __init__(self, leagues: dict = None):
        self.sports = Sports()

        if leagues:
            self.leagues = leagues
            return

        self.leagues = {
            'Russia': 'https://1xstavka.ru/line/Football/225733-Russia-Premier-League/',
            'England': 'https://1xstavka.ru/line/Football/88637-England-Premier-League/',
            'France': 'https://1xstavka.ru/line/Football/12821-France-Ligue-1/',
            'Germany': 'https://1xstavka.ru/line/Football/96463-Germany-Bundesliga/',
            'Spain': 'https://1xstavka.ru/line/Football/127733-Spain-La-Liga/',
            'Netherlands': 'https://1xstavka.ru/line/Football/2018750-Netherlands-Eredivisie/',
            'Championship': 'https://1xstavka.ru/line/Football/105759-England-Championship/',
            'Turkey': 'https://1xstavka.ru/line/Football/11113-Turkey-SuperLiga/',
            'Italy': 'https://1xstavka.ru/line/Football/110163-Italy-Serie-A/',
            'Portugal': 'https://1xstavka.ru/line/Football/118663-Portugal-Primeira-Liga/',
            'UEFA_1': 'https://1xstavka.ru/line/Football/118587-UEFA-Champions-League/',
            'UEFA_2': 'https://1xstavka.ru/line/Football/118593-UEFA-Europa-League/',
        }

    async def __update_match(self, league_name: str, match_info: dict, cur_round: bool = False) -> bool:
        db_session: SQLSession = Session()
        html_session = AsyncHTMLSession()
        try:
            home_team = match_info['homeTeam']['name']
            away_team = match_info['awayTeam']['name']
            match_url = match_info['url']

            logging.info(f"Update coeffs in match {home_team} vs {away_team}")

            # not match
            if "голы" in home_team or "специальное" in home_team or "Хозяева" in home_team:
                return False

            n_att = 0
            while n_att < 3:
                try:
                    r = await html_session.get(match_url)
                except requests.exceptions.ConnectionError:
                    n_att += 1
                    sleep(5)
                    continue
            if n_att == 3:
                return False

            # render JS
            try:
                await r.html.arender(retries=2, wait=0.5, timeout=10)
            except:
                await r.html.arender(retries=1, wait=1.5, timeout=40)

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
            home_coeff = Coeff(
                home_team, away_team, league_name,
                total_1_more_1_5, total_2_less_0_5, True, cur_round
            )
            away_coeff = Coeff(
                away_team, home_team, league_name,
                total_2_more_1_5, total_1_less_0_5, False, cur_round
            )
            db_session.add_all([home_coeff, away_coeff])
            return True
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:           
            await html_session.close()
            db_session.commit()
            db_session.close()

    async def update_league(self, league_name: str) -> bool:
        logging.info(f"Update coeffs in league={league_name}")

        if league_name not in self.leagues:
            return False

        try:
            response = requests.get(self.leagues[league_name])
            soup = BeautifulSoup(response.text, 'lxml')

            all_matches = json.loads("".join(soup.find("script", {"type": "application/ld+json"}).contents))

            if len(all_matches) == 0:
                return False

            cur_round_matches = self.sports.get_games_count(league_name)
            updated_matches = 0
            checked_matches = 0
            # update cur round
            while updated_matches < cur_round_matches:
                if await self.__update_match(league_name, all_matches[checked_matches], True):
                    updated_matches += 1
                checked_matches += 1
            # update next round
            while checked_matches < len(all_matches):
                await self.__update_match(league_name, all_matches[checked_matches], False)
                checked_matches += 1

            return True
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False

    def update_all(self) -> bool:
        return all(list(map(lambda x: self.update_league(x), self.leagues)))


if __name__ == "__main__":
    xbet = XBet()
    xbet.update_all()
