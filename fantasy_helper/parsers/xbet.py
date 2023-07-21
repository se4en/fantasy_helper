import logging
import sys
import os
import json
import typing as t

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


class XbetParser:
    def __init__(self, leagues: t.List[LeagueInfo]):
        self.__leagues = {l.name: l.xber_url for l in leagues if l.xber_url is not None}

    @staticmethod
    def __parse_bet_value(all_bets: t.Any, bet_name: str) -> float:
        bet = WebDriverWait(all_bets, 3).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//*[contains(text(), '{bet_name}')]/../*[@class='koeff']")
            )
        )
        return float(bet.get_attribute("data-coef"))

    @staticmethod
    def __parse_match(match_info: MatchInfo) -> MatchInfo:
        driver = None
        try:
            driver = webdriver.Firefox()
            driver.get(match_info.url)

            match_info.total_1_over_1_5 = XbetParser.__parse_bet_value(
                driver, "Individual Total 1 Over 1.5"
            )
            match_info.total_1_under_0_5 = XbetParser.__parse_bet_value(
                driver, "Individual Total 1 Under 0.5"
            )
            match_info.total_2_over_1_5 = XbetParser.__parse_bet_value(
                driver, "Individual Total 2 Over 1.5"
            )
            match_info.total_2_under_0_5 = XbetParser.__parse_bet_value(
                driver, "Individual Total 2 Under 0.5"
            )
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            if driver is not None:
                driver.close()
            return match_info

    @staticmethod
    def __filter_matches(all_matches: t.Any) -> t.List[MatchInfo]:
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

    def __parse_league_matches(self, league_name: str) -> t.Optional[t.List[MatchInfo]]:
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

        result = XbetParser.__filter_matches(all_matches)
        if result:
            return result
        else:
            return None

    def get_league_matches(self, league_name: str) -> t.List[MatchInfo]:
        result = []
        league_matches = self.__parse_league_matches(league_name)
        if league_matches is not None:
            for match in league_matches:
                parsed_match = self.__parse_match(match)
                if (
                    parsed_match.total_1_over_1_5 is not None
                    or parsed_match.total_1_under_0_5 is not None
                    or parsed_match.total_2_over_1_5 is not None
                    or parsed_match.total_2_under_0_5 is not None
                ):
                    result.append(parsed_match)

        return result