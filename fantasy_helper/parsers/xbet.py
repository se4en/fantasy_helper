import datetime
import logging
import sys
import os
import json
import pytz
from typing import Any, Dict, List, Optional

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import FirefoxOptions

from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


class XbetParser:
    def __init__(self, leagues: List[LeagueInfo]):
        self._leagues = {
            l.name: l.xber_url
            for l in leagues
            if l.xber_url is not None and l.is_active
        }

    @staticmethod
    def _parse_start_datetime(driver: Any) -> datetime.datetime:
        start_datetime = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "c-scoreboard-start__date"))
        )
        date, time = start_datetime.text.strip().split()
        if "/" in date:
            day, month, year = date.split("/")
        else:
            day, month, year = date.split(".")
        hour, minute = time.split(":")

        return datetime.datetime(
            int(year), int(month), int(day), int(hour), int(minute), tzinfo=pytz.UTC
        )

    @staticmethod
    def _parse_bets_values(driver: Any) -> Dict[str, Dict[str, float]]:
        bet_groups = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "bet_group"))
        )

        result = {}
        for i, bet_group in enumerate(bet_groups):
            driver.execute_script("arguments[0].scrollIntoView(true);", bet_group)

            bet_lines = bet_group.text.split("\n")
            if len(bet_lines) == 0:
                continue

            bet_group_name = bet_lines[0]

            bets_values = {}
            bet_name, bet_value = None, None
            for bet_line in bet_lines[1:]:
                if bet_name is None:
                    bet_name = bet_line.strip()
                else:
                    try:
                        bet_value = float(bet_line.strip())
                        bets_values[bet_name] = bet_value
                        bet_name, bet_value = None, None
                    except ValueError:
                        pass

            result[bet_group_name] = bets_values

        return result

    @staticmethod
    def _parse_match(match_info: MatchInfo) -> MatchInfo:
        driver = None
        try:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
            opts.add_argument("--disable-blink-features=AutomationControlled")
            driver = webdriver.Firefox(
                executable_path=os.environ["GECKODRIVER_PATH"], options=opts
            )
            driver.get(match_info.url)

            match_info.start_datetime = XbetParser._parse_start_datetime(driver)

            bets_values = XbetParser._parse_bets_values(driver)
            match_info.total_1_over_1_5 = bets_values.get("Индивидуальный тотал 1-го", {}).get("1.5 Б")
            match_info.total_1_under_0_5 = bets_values.get("Индивидуальный тотал 1-го", {}).get("0.5 М")
            match_info.total_2_over_1_5 = bets_values.get("Индивидуальный тотал 2-го", {}).get("1.5 Б")
            match_info.total_2_under_0_5 = bets_values.get("Индивидуальный тотал 2-го", {}).get("0.5 М")
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            if driver is not None:
                driver.quit()

            return match_info

    @staticmethod
    def _filter_matches(all_matches: Any, league_name: str) -> List[MatchInfo]:
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
                        url=match_info["url"],
                        league_name=league_name,
                        home_team=match_info["homeTeam"]["name"],
                        away_team=match_info["awayTeam"]["name"],
                    )
                )
        return result

    def _parse_league_matches(self, league_name: str) -> Optional[List[MatchInfo]]:
        if league_name not in self._leagues:
            return None

        driver = None
        try:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
            opts.add_argument("--disable-blink-features=AutomationControlled")

            driver = webdriver.Firefox(
                executable_path=os.environ["GECKODRIVER_PATH"], options=opts
            )
            driver.get(self._leagues[league_name])

            all_matches = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "c-events__teams"))
            )

            result = []
            for match in all_matches:
                team_names = match.get_attribute("title").split("—")
                match_url = match.find_element(By.XPATH, "..").get_attribute("href")
                result.append(
                    MatchInfo(
                        url=match_url,
                        league_name=league_name,
                        home_team=team_names[0].strip(),
                        away_team=team_names[1].strip(),
                    )
                )
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            if driver is not None:
                driver.quit()

            return result

    def get_league_matches(self, league_name: str) -> List[MatchInfo]:
        result = []
        league_matches = self._parse_league_matches(league_name)
        if league_matches is not None:
            for match in league_matches:
                parsed_match = self._parse_match(match)
                if (
                    parsed_match.total_1_over_1_5 is not None
                    or parsed_match.total_1_under_0_5 is not None
                    or parsed_match.total_2_over_1_5 is not None
                    or parsed_match.total_2_under_0_5 is not None
                ):
                    result.append(parsed_match)

        return result
