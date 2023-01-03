from dataclasses import dataclass
import logging
import sys
import os
import json
from typing import Any, Dict, List, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
import requests
from bs4 import BeautifulSoup


@dataclass
class MatchInfo:
    url: str
    home_team: str
    away_team: str
    total_1_over_1_5: Optional[float] = None
    total_1_under_0_5: Optional[float] = None
    total_2_over_1_5: Optional[float] = None
    total_2_under_0_5: Optional[float] = None


class XbetParser:
    def __init__(self, leagues: Optional[Dict[str, str]] = None, delay: int = 3):
        self._delay = delay

        if leagues:
            self.leagues = leagues
            return

        self.leagues = {
            "Russia": "https://1xstavka.ru/line/football/225733-russia-premier-league",
            # "England": "https://1xstavka.ru/line/Football/88637-England-Premier-League/",
            # "France": "https://1xstavka.ru/line/Football/12821-France-Ligue-1/",
            # "Germany": "https://1xstavka.ru/line/Football/96463-Germany-Bundesliga/",
            # "Spain": "https://1xstavka.ru/line/Football/127733-Spain-La-Liga/",
            # "Netherlands": "https://1xstavka.ru/line/Football/2018750-Netherlands-Eredivisie/",
            # "Championship": "https://1xstavka.ru/line/Football/105759-England-Championship/",
            # "Turkey": "https://1xstavka.ru/line/Football/11113-Turkey-SuperLiga/",
            # "Italy": "https://1xstavka.ru/line/Football/110163-Italy-Serie-A/",
            # "Portugal": "https://1xstavka.ru/line/Football/118663-Portugal-Primeira-Liga/",
            # "UEFA_1": "https://1xstavka.ru/line/Football/118587-UEFA-Champions-League/",
            # "UEFA_2": "https://1xstavka.ru/line/Football/118593-UEFA-Europa-League/",
        }

    def _parse_bet_value(self, all_bets: Any, bet_name: str) -> float:
        return float(
            all_bets.find_element(
                By.XPATH,
                f"//*[contains(text(), '{bet_name}')]/../*[@class='koeff']",
            ).get_attribute("data-coef")
        )

    def _parse_match(self, match_info: MatchInfo) -> MatchInfo:
        try:
            driver = webdriver.Firefox()
            driver.get(match_info.url)

            all_bets = driver.find_element(By.ID, "allBetsTable")
            match_info.total_1_over_1_5 = self._parse_bet_value(
                all_bets, "Individual Total 1 Over 1.5"
            )
            match_info.total_1_under_0_5 = self._parse_bet_value(
                all_bets, "Individual Total 1 Under 0.5"
            )
            match_info.total_2_over_1_5 = self._parse_bet_value(
                all_bets, "Individual Total 2 Over 1.5"
            )
            match_info.total_2_under_0_5 = self._parse_bet_value(
                all_bets, "Individual Total 2 Under 0.5"
            )
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            driver.close()
            return match_info

    # @staticmethod
    def _filter_matches(self, all_matches: Any) -> List[MatchInfo]:
        result = []
        for match_info in all_matches:
            if (
                "url" in match_info
                and "homeTeam" in match_info
                and "name" in match_info["homeTeam"]
                and "awayTeam" in match_info
                and "name" in match_info["awayTeam"]
            ):
                result.append(
                    MatchInfo(
                        match_info["url"],
                        match_info["homeTeam"]["name"],
                        match_info["awayTeam"]["name"],
                    )
                )
        return result

    def _parse_league_matches(self, league_name: str) -> Optional[List[MatchInfo]]:
        if league_name not in self.leagues:
            return None

        try:
            response = requests.get(self.leagues[league_name])
            soup = BeautifulSoup(response.text, "lxml")

            all_matches = json.loads(
                "".join(soup.find("script", {"type": "application/ld+json"}).contents)
            )
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return None

        result = self._filter_matches(all_matches)
        if result:
            return result
        else:
            return None

    def parse_league(self, league_name: str) -> Optional[List[MatchInfo]]:
        league_matches = self._parse_league_matches(league_name)
        if league_matches is not None:
            return list(map(self._parse_match, league_matches))
        else:
            return None


if __name__ == "__main__":
    parser = XbetParser()
    print(parser.parse_league("Russia"))
