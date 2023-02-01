import logging
import sys
import os
import json
import typing as t

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


class XbetParser:
    def __init__(self, leagues: t.List[LeagueInfo]):
        self.__leagues = {l.name: l.xber_url for l in leagues if l.xber_url is not None}

    @staticmethod
    def _parse_bet_value(all_bets: t.Any, bet_name: str) -> float:
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
            match_info.total_1_over_1_5 = self.__class__._parse_bet_value(
                all_bets, "Individual Total 1 Over 1.5"
            )
            match_info.total_1_under_0_5 = self.__class__._parse_bet_value(
                all_bets, "Individual Total 1 Under 0.5"
            )
            match_info.total_2_over_1_5 = self.__class__._parse_bet_value(
                all_bets, "Individual Total 2 Over 1.5"
            )
            match_info.total_2_under_0_5 = self.__class__._parse_bet_value(
                all_bets, "Individual Total 2 Under 0.5"
            )
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            driver.close()
            return match_info

    @staticmethod
    def _filter_matches(all_matches: t.Any) -> t.List[MatchInfo]:
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

    def _parse_league_matches(self, league_name: str) -> t.Optional[t.List[MatchInfo]]:
        if league_name not in self.__leagues:
            return None

        try:
            response = requests.get(self.__leagues[league_name])
            soup = BeautifulSoup(response.text, "lxml")

            all_matches = json.loads(
                "".join(soup.find("script", {"type": "application/ld+json"}).contents)
            )
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return None

        result = self.__class__._filter_matches(all_matches)
        if result:
            return result
        else:
            return None

    def parse_league(self, league_name: str) -> t.Optional[t.List[MatchInfo]]:
        league_matches = self._parse_league_matches(league_name)
        if league_matches is not None:
            return list(map(self._parse_match, league_matches))
        else:
            return None
