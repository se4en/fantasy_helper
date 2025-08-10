import datetime
import logging
import sys
import os
import json
import time
import pytz
from typing import Any, Dict, List, Optional, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver import FirefoxOptions
from selenium.common.exceptions import WebDriverException, TimeoutException
from loguru import logger

from fantasy_helper.conf.config import PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASSWORD
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


class BetcityParser:
    def __init__(self, leagues: List[LeagueInfo]):
        self._leagues = {
            l.name: l.betcity_url
            for l in leagues
            if l.betcity_url is not None and l.is_active
        }

        self._bet_group_methods = {
            "ОБЕ ЗАБЬЮТ": self._parse_both_scores_bets,
            "ТОТАЛ": self._parse_total_bets,
            "ФОРА": self._parse_handicap_bets,
            "ИНДИВИДУАЛЬНЫЙ ТОТАЛ": self._parse_individual_total_bets,
            "ГОЛЫ": self._parse_goals_bets
        }
        
        self._max_retries = 3
        self._retry_delay = 10  # seconds - increased delay
        self._page_timeout = 60  # seconds - increased timeout

    def _create_driver(self, use_proxy: bool = True) -> webdriver.Firefox:
        """Create a Firefox driver with optional proxy configuration."""
        opts = FirefoxOptions()
        opts.add_argument("--headless")
        opts.add_argument("--disable-blink-features=AutomationControlled")
        
        # Add user agent to avoid detection
        opts.set_preference("general.useragent.override", 
                          "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0")                                                                                                                                                                            
        opts.set_preference("network.http.accept.default", "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8")                                                                                                         
        opts.set_preference("network.http.accept-language.default", "en-US,en;q=0.5")

        # Set timeouts - increase for better reliability
        opts.set_preference("network.http.connection-timeout", 60)
        opts.set_preference("network.http.response.timeout", 60)
        opts.set_preference("dom.max_script_run_time", 60)
        opts.set_preference("dom.max_chrome_script_run_time", 60)
        
        # Disable images and CSS for faster loading
        opts.set_preference("permissions.default.image", 2)
        opts.set_preference("permissions.default.stylesheet", 2)
        
        # Disable JavaScript (if not needed for basic content)
        # opts.set_preference("javascript.enabled", False)
        
        if use_proxy and PROXY_HOST and PROXY_PORT and PROXY_USER and PROXY_PASSWORD:
            proxy_url = f"http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"
            proxy = Proxy({
                'proxyType': ProxyType.MANUAL,
                'httpProxy': proxy_url,
                'ftpProxy': proxy_url,
                'sslProxy': proxy_url,
                'noProxy': ''
            })
            return webdriver.Firefox(
                executable_path=os.environ["GECKODRIVER_PATH"], 
                options=opts, 
                proxy=proxy
            )
        else:
            return webdriver.Firefox(
                executable_path=os.environ["GECKODRIVER_PATH"], 
                options=opts
            )

    def _parse_league_matches(self, league_name: str) -> Optional[List[MatchInfo]]:
        if league_name not in self._leagues:
            return None

        result = []
        driver = None
        use_proxy = True

        for attempt in range(self._max_retries):
            try:
                driver = self._create_driver(use_proxy=use_proxy)
                driver.set_page_load_timeout(self._page_timeout)
                
                logger.info(f"Attempt {attempt + 1}: Getting league matches from {self._leagues[league_name]} (proxy: {use_proxy})")
                driver.get(self._leagues[league_name])
                time.sleep(3)
                champ_line = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "line__champ"))
                )
                
                if champ_line is None:
                    logger.warning(f"Attempt {attempt + 1} failed: No matches found on page {self._leagues[league_name]}")
                    continue
            
                all_matches = champ_line.find_elements(By.CLASS_NAME, "line-event")
                for match in all_matches:
                    match_name_elem = match.find_element(By.CLASS_NAME, "line-event__name")
                    match_url = match_name_elem.get_attribute("href")
                    match_teams_names = match_name_elem.find_elements(By.TAG_NAME, "b")
                    if len(match_teams_names) != 2:
                        continue
                    home_team_name = match_teams_names[0].text.strip()
                    away_team_name = match_teams_names[1].text.strip()

                    result.append(
                        MatchInfo(
                            url=match_url,
                            league_name=league_name,
                            home_team=home_team_name,
                            away_team=away_team_name,
                        )
                    )

                if result:
                    logger.info(f"Successfully parsed {len(result)} matches")
                    break  # Success, exit retry loop
                else:
                    logger.warning("No matches were successfully parsed")
                
            except (WebDriverException, TimeoutException) as ex:
                logger.warning(f"Attempt {attempt + 1} failed for league {league_name}: {str(ex)}")
                if attempt < self._max_retries - 1:
                    logger.info(f"Retrying in {self._retry_delay} seconds...")
                    time.sleep(self._retry_delay)
                else:
                    logger.error(f"All {self._max_retries} attempts failed for league {league_name}")
            except Exception as ex:
                logger.exception("An unexpected error while parsing betcity league matches")
                break
            finally:
                if driver is not None:
                    driver.quit()
                    driver = None

        return result

    @staticmethod
    def _add_both_scores_value(match_info: MatchInfo, type: str, value: float) -> MatchInfo:
        if type == "Да":
            match_info.both_score_yes = value
        elif type == "Нет":
            match_info.both_score_no = value
        return match_info
    
    def _parse_both_scores_bets(self, bet_group: Any, match_info: MatchInfo) -> MatchInfo:
        group_blocks = bet_group.find_elements(By.CLASS_NAME, "dops-item-row__block")
        if len(group_blocks) != 2:
            return match_info

        type_1 = group_blocks[0].find_element(By.CLASS_NAME, "dops-item-row__block-left").text.strip()
        value_1 = float(group_blocks[0].find_element(By.CLASS_NAME, "dops-item-row__block-right").text.strip())
        type_2 = group_blocks[1].find_element(By.CLASS_NAME, "dops-item-row__block-left").text.strip()
        value_2 = float(group_blocks[1].find_element(By.CLASS_NAME, "dops-item-row__block-right").text.strip())

        match_info = self._add_both_scores_value(match_info, type_1, value_1)
        match_info = self._add_both_scores_value(match_info, type_2, value_2)

        return match_info

    @staticmethod
    def _add_total_bet_value(match_info: MatchInfo, base: str, type: str, value: float) -> MatchInfo:
        if base == "0.5" and type == "Мен":
            match_info.total_under_0_5 = value
        elif base == "0.5" and type == "Бол":
            match_info.total_over_0_5 = value
        elif base == "1" and type == "Мен":
            match_info.total_under_1 = value
        elif base == "1" and type == "Бол":
            match_info.total_over_1 = value
        elif base == "1.5" and type == "Мен":
            match_info.total_under_1_5 = value
        elif base == "1.5" and type == "Бол":
            match_info.total_over_1_5 = value
        elif base == "2" and type == "Мен":
            match_info.total_under_2 = value
        elif base == "2" and type == "Бол":
            match_info.total_over_2 = value
        elif base == "2.5" and type == "Мен":
            match_info.total_under_2_5 = value
        elif base == "2.5" and type == "Бол":
            match_info.total_over_2_5 = value
        elif base == "3" and type == "Мен":
            match_info.total_under_3 = value
        elif base == "3" and type == "Бол":
            match_info.total_over_3 = value
        elif base == "3.5" and type == "Мен":
            match_info.total_under_3_5 = value
        elif base == "3.5" and type == "Бол":
            match_info.total_over_3_5 = value
        elif base == "4" and type == "Мен":
            match_info.total_under_4 = value
        elif base == "4" and type == "Бол":
            match_info.total_over_4 = value
        elif base == "4.5" and type == "Мен":
            match_info.total_under_4_5 = value
        elif base == "4.5" and type == "Бол":
            match_info.total_over_4_5 = value
        return match_info
    
    def _parse_total_bets(self, bet_group: Any, match_info: MatchInfo) -> MatchInfo:
        group_rows = bet_group.find_elements(By.CLASS_NAME, "dops-item-row__section")
        for group_row in group_rows:
            row_blocks = group_row.find_elements(By.CLASS_NAME, "dops-item-row__block")

            if len(row_blocks) < 2:
                continue

            base = row_blocks[0].text.strip()
            for row_block in row_blocks[1:]:
                type = row_block.find_element(By.CLASS_NAME, "dops-item-row__block-left").text.strip()
                value = float(row_block.find_element(By.CLASS_NAME, "dops-item-row__block-right").text.strip())
                match_info = self._add_total_bet_value(match_info, base, type, value)

        return match_info

    @staticmethod
    def _parse_handicap_base_type(base_type: str) -> Tuple[str, str]:
        base, type = base_type.split(" ")
        return base.strip(), type[1:-1].strip()

    @staticmethod
    def _add_handicap_bet_value(match_info: MatchInfo, base: str, type: str, value: float) -> MatchInfo:
        if base == "Ф1" and type == "-2.5":
            match_info.handicap_1_minus_2_5 = value
        elif base == "Ф1" and type == "-2":
            match_info.handicap_1_minus_2 = value
        elif base == "Ф1" and type == "-1.5":
            match_info.handicap_1_minus_1_5 = value
        elif base == "Ф1" and type == "-1":
            match_info.handicap_1_minus_1 = value
        elif base == "Ф1" and type == "0":
            match_info.handicap_1_0 = value
        elif base == "Ф1" and type == "+1":
            match_info.handicap_1_plus_1 = value
        elif base == "Ф1" and type == "+1.5":
            match_info.handicap_1_plus_1_5 = value
        elif base == "Ф1" and type == "+2":
            match_info.handicap_1_plus_2 = value
        elif base == "Ф1" and type == "+2.5":
            match_info.handicap_1_plus_2_5 = value
        elif base == "Ф2" and type == "-2.5":
            match_info.handicap_2_minus_2_5 = value
        elif base == "Ф2" and type == "-2":
            match_info.handicap_2_minus_2 = value
        elif base == "Ф2" and type == "-1.5":
            match_info.handicap_2_minus_1_5 = value
        elif base == "Ф2" and type == "-1":
            match_info.handicap_2_minus_1 = value
        elif base == "Ф2" and type == "0":
            match_info.handicap_2_0 = value
        elif base == "Ф2" and type == "+1":
            match_info.handicap_2_plus_1 = value
        elif base == "Ф2" and type == "+1.5":
            match_info.handicap_2_plus_1_5 = value
        elif base == "Ф2" and type == "+2":
            match_info.handicap_2_plus_2 = value
        elif base == "Ф2" and type == "+2.5":
            match_info.handicap_2_plus_2_5 = value
        return match_info
    
    def _parse_handicap_bets(self, bet_group: Any, match_info: MatchInfo) -> MatchInfo:
        group_rows = bet_group.find_elements(By.CLASS_NAME, "dops-item-row__section")
        for group_row in group_rows:
            row_blocks = group_row.find_elements(By.CLASS_NAME, "dops-item-row__block")

            if len(row_blocks) == 0:
                continue

            for row_block in row_blocks:
                base_type = row_block.find_element(By.CLASS_NAME, "dops-item-row__block-left").text.strip()
                value = float(row_block.find_element(By.CLASS_NAME, "dops-item-row__block-right").text.strip())
                base, type = self._parse_handicap_base_type(base_type)
                match_info = self._add_handicap_bet_value(match_info, base, type, value)

        return match_info

    @staticmethod
    def _parse_individual_total_base_type(base_type: str) -> Tuple[str, str]:
        base, type = base_type.split(" ")
        return base.strip(), type[1:-1].strip()

    @staticmethod
    def _add_individual_total_bet_value(match_info: MatchInfo, base: str, type: str, subtype: str, value: float) -> MatchInfo:
        if base == "ИТ1" and type == "1" and subtype == "Бол":
            match_info.total_1_over_1 = value
        elif base == "ИТ1" and type == "1.5" and subtype == "Бол":
            match_info.total_1_over_1_5 = value
        elif base == "ИТ1" and type == "2" and subtype == "Бол":
            match_info.total_1_over_2 = value
        elif base == "ИТ1" and type == "2.5" and subtype == "Бол":
            match_info.total_1_over_2_5 = value
        elif base == "ИТ1" and type == "1" and subtype == "Мен":
            match_info.total_1_under_1 = value
        elif base == "ИТ1" and type == "1.5" and subtype == "Мен":
            match_info.total_1_under_1_5 = value
        elif base == "ИТ1" and type == "2" and subtype == "Мен":
            match_info.total_1_under_2 = value
        elif base == "ИТ1" and type == "2.5" and subtype == "Мен":
            match_info.total_1_under_2_5 = value
        elif base == "ИТ2" and type == "1" and subtype == "Бол":
            match_info.total_2_over_1 = value
        elif base == "ИТ2" and type == "1.5" and subtype == "Бол":
            match_info.total_2_over_1_5 = value
        elif base == "ИТ2" and type == "2" and subtype == "Бол":
            match_info.total_2_over_2 = value
        elif base == "ИТ2" and type == "2.5" and subtype == "Бол":
            match_info.total_2_over_2_5 = value
        elif base == "ИТ2" and type == "1" and subtype == "Мен":
            match_info.total_2_under_1 = value
        elif base == "ИТ2" and type == "1.5" and subtype == "Мен":
            match_info.total_2_under_1_5 = value
        elif base == "ИТ2" and type == "2" and subtype == "Мен":
            match_info.total_2_under_2 = value
        elif base == "ИТ2" and type == "2.5" and subtype == "Мен":
            match_info.total_2_under_2_5 = value
        return match_info

    def _parse_individual_total_bets(self, bet_group: Any, match_info: MatchInfo) -> MatchInfo:
        group_rows = bet_group.find_elements(By.CLASS_NAME, "dops-item-row__section")
        for group_row in group_rows:
            row_blocks = group_row.find_elements(By.CLASS_NAME, "dops-item-row__block")

            if len(row_blocks) < 2:
                continue

            base_type = row_blocks[0].text.strip()
            base, type = self._parse_handicap_base_type(base_type)
            for row_block in row_blocks[1:]:
                subtype = row_block.find_element(By.CLASS_NAME, "dops-item-row__block-left").text.strip()
                value = float(row_block.find_element(By.CLASS_NAME, "dops-item-row__block-right").text.strip())
                match_info = self._add_individual_total_bet_value(match_info, base, type, subtype, value)

        return match_info

    @staticmethod
    def _add_goals_bet_value(match_info: MatchInfo, base: str, type: str, value: float) -> MatchInfo:
        if base == "К1" and type == "Забьет":
            match_info.total_1_over_0_5 = value
        elif base == "К1" and type == "Не забьет":
            match_info.total_1_under_0_5 = value
        elif base == "К2" and type == "Забьет":
            match_info.total_2_over_0_5 = value
        elif base == "К2" and type == "Не забьет":
            match_info.total_2_under_0_5 = value
        return match_info

    def _parse_goals_bets(self, bet_group: Any, match_info: MatchInfo) -> MatchInfo:
        group_rows = bet_group.find_elements(By.CLASS_NAME, "dops-item-row__section")
        for group_row in group_rows:
            row_blocks = group_row.find_elements(By.CLASS_NAME, "dops-item-row__block")

            if len(row_blocks) < 2:
                continue

            base = row_blocks[0].text.strip()
            for row_block in row_blocks[1:]:
                type = row_block.find_element(By.CLASS_NAME, "dops-item-row__block-left").text.strip()
                value = float(row_block.find_element(By.CLASS_NAME, "dops-item-row__block-right").text.strip())
                match_info = self._add_goals_bet_value(match_info, base, type, value)

        return match_info
    
    def _parse_main_bets(self, driver: Any, match_info: MatchInfo) -> MatchInfo:
        bet_groups = WebDriverWait(driver, 3).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "dops-item"))
        )

        for bet_group in bet_groups:
            group_title = bet_group.find_element(By.CLASS_NAME, "dops-item__title").text.strip()
            if group_title in self._bet_group_methods:
                match_info = self._bet_group_methods[group_title](bet_group, match_info)

        return match_info

    @staticmethod
    def _add_header_bet_value(
        match_info: MatchInfo,
        cur_title: str,
        cur_value: str, 
        prev_title: Optional[str] = None, 
        prev_value: Optional[str] = None,
        prev_prev_title: Optional[str] = None, 
        prev_prev_value: Optional[str] = None
    ) -> MatchInfo:
        if cur_title == "1":
            match_info.result_1 = float(cur_value)
        elif cur_title == "X":
            match_info.result_x = float(cur_value)
        elif cur_title == "2":
            match_info.result_2 = float(cur_value)
        elif prev_title is not None and (prev_title == "Ф1" or prev_title == "Ф2"):
            match_info = BetcityParser._add_handicap_bet_value(
                match_info=match_info, 
                base=prev_title, 
                type=prev_value, 
                value=float(cur_value)
            )
        elif prev_title is not None and prev_title == "ТОТ":
            if cur_title == "М":
                match_info = BetcityParser._add_total_bet_value(
                    match_info=match_info, 
                    base=prev_value, 
                    type="Мен", 
                    value=float(cur_value)
                )
            elif cur_title == "Б":
                match_info = BetcityParser._add_total_bet_value(
                    match_info=match_info, 
                    base=prev_value, 
                    type="Бол", 
                    value=float(cur_value)
                )
        elif prev_prev_title is not None and prev_prev_title == "ТОТ":
            if prev_title == "М":
                match_info = BetcityParser._add_total_bet_value(
                    match_info=match_info, 
                    base=prev_prev_value, 
                    type="Мен", 
                    value=float(cur_value)
                )
            elif prev_title == "Б":
                match_info = BetcityParser._add_total_bet_value(
                    match_info=match_info, 
                    base=prev_prev_value, 
                    type="Бол", 
                    value=float(cur_value)
                )
        return match_info
    
    def _parse_header_bets_titles(self, line_header: Any) -> List[str]:
        header_items = line_header.find_elements(By.CLASS_NAME, "line__header-item_dop")
        result = []
        for header_item in header_items:
            result.append(header_item.text.strip())
        return result

    def _parse_header_bets_values(self, main_bets: Any) -> List[str]:
        bets_buttons = main_bets.find_elements(By.CLASS_NAME, "line-event__main-bets-button")
        result = []
        for bet_button in bets_buttons:
            result.append(bet_button.text.strip())
        return result

    def _merge_header_bets(self, bets_titles: Any, bets_values: Any, match_info: MatchInfo) -> MatchInfo:
        if len(bets_titles) != len(bets_values):
            return match_info

        prev_title, prev_value = None, None
        prev_prev_title, prev_prev_value = None, None
        for i in range(len(bets_titles)):
            match_info = self._add_header_bet_value(
                match_info,
                bets_titles[i],
                bets_values[i],
                prev_title,
                prev_value,
                prev_prev_title,
                prev_prev_value
            )
            prev_prev_title, prev_prev_value = prev_title, prev_value
            prev_title, prev_value = bets_titles[i], bets_values[i]

        return match_info

    def _parse_header_bets(self, driver: Any, match_info: MatchInfo) -> MatchInfo:
        line_header = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "line__header"))
        )
        main_bets = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CLASS_NAME, "line-event__main-bets"))
        )

        bets_titles = self._parse_header_bets_titles(line_header)
        bets_values = self._parse_header_bets_values(main_bets)
        match_info = self._merge_header_bets(bets_titles, bets_values, match_info)

        return match_info

    def _parse_match(self, match_info: MatchInfo) -> MatchInfo:
        driver = None
        
        for attempt in range(self._max_retries):
            try:
                # Try with proxy first, then without if it fails
                use_proxy = attempt == 0
                driver = self._create_driver(use_proxy=use_proxy)
                driver.set_page_load_timeout(self._page_timeout)
                
                logger.info(f"Attempt {attempt + 1}: Parsing match {match_info.url} (proxy: {use_proxy})")
                driver.get(match_info.url)

                match_info = self._parse_header_bets(driver, match_info)
                match_info = self._parse_main_bets(driver, match_info)
                break  # Success, exit retry loop
                
            except (WebDriverException, TimeoutException) as ex:
                logger.warning(f"Attempt {attempt + 1} failed for match {match_info.url}: {str(ex)}")
                if attempt < self._max_retries - 1:
                    logger.info(f"Retrying in {self._retry_delay} seconds...")
                    time.sleep(self._retry_delay)
                else:
                    logger.error(f"All {self._max_retries} attempts failed for match {match_info.url}")
            except Exception as ex:
                logger.exception("An unexpected error while parsing betcity match")
                break
            finally:
                if driver is not None:
                    driver.quit()
                    driver = None

        return match_info

    def get_league_matches(self, league_name: str) -> List[MatchInfo]:
        result = []
        logger.info(f"get betcity matches for {league_name}")
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
