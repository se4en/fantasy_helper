import asyncio
import datetime
import logging
import random
import sys
import os
import json
import time
import pytz
from typing import Any, Dict, List, Optional, Tuple

from playwright.async_api import async_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
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
            "обе забьют": self._parse_both_scores_bets,
            "тотал": self._parse_total_bets,
            "фора": self._parse_handicap_bets,
            "индивидуальный тотал": self._parse_individual_total_bets,
            "голы": self._parse_goals_bets
        }
        
        self._use_random_port = False
        self._max_retries = 3
        self._retry_delay = 10  # seconds - increased delay
        self._page_timeout = 60  # seconds - increased timeout

    async def _create_browser_context(self, use_proxy: bool = True) -> tuple[Browser, BrowserContext]:
        """Create a Playwright browser context with optional proxy configuration."""
        playwright = await async_playwright().start()
        
        # Browser launch options
        launch_options = {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor"
            ]
        }
        
        USER_AGENTS = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        ]
        user_agent = USER_AGENTS[random.randint(0, len(USER_AGENTS) - 1)]
        # Context options
        context_options = {
            "user_agent": user_agent,
            "extra_http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5"
            },
            "viewport": {"width": 1920, "height": 1080}
        }
        
        # Add proxy if configured
        if use_proxy and PROXY_HOST and PROXY_PORT and PROXY_USER and PROXY_PASSWORD:
            # get random proxy port from 10001 to 10999
            if self._use_random_port:
                proxy_port = str(random.randint(10001, 10999))
            else:
                proxy_port = PROXY_PORT
            context_options["proxy"] = {
                "server": f"http://{PROXY_HOST}:{proxy_port}",
                "username": PROXY_USER,
                "password": PROXY_PASSWORD
            }
        
        browser = await playwright.chromium.launch(**launch_options)
        context = await browser.new_context(**context_options)
        
        # Block images and CSS for faster loading
        await context.route("**/*.{png,jpg,jpeg,gif,svg,css}", lambda route: route.abort())
        
        return browser, context

    async def _parse_league_matches(self, league_name: str) -> Optional[List[MatchInfo]]:
        if league_name not in self._leagues:
            return None

        result = []
        browser = None
        context = None
        use_proxy = True

        for attempt in range(self._max_retries):
            try:
                browser, context = await self._create_browser_context(use_proxy=use_proxy)
                page = await context.new_page()
                page.set_default_timeout(self._page_timeout * 1000)  # Playwright uses milliseconds
                
                logger.info(f"Attempt {attempt + 1}: Getting league matches from {self._leagues[league_name]} (proxy: {use_proxy})")
                await page.goto(self._leagues[league_name])
                await page.wait_for_timeout(3000)  # 3 seconds

                champ_line = await page.wait_for_selector(".line__champ", timeout=10000)
                if champ_line is None:
                    logger.warning(f"Attempt {attempt + 1} failed: No matches found on page {self._leagues[league_name]}")
                    continue
            
                all_matches = await champ_line.query_selector_all(".line-event")
                for match in all_matches:
                    match_name_elem = await match.query_selector(".line-event__name")
                    if match_name_elem is None:
                        continue
                    
                    match_url = await match_name_elem.get_attribute("href")
                    match_teams_names = await match_name_elem.query_selector_all("b")
                    if len(match_teams_names) != 2:
                        continue
                    
                    home_team_name = (await match_teams_names[0].text_content()).strip()
                    away_team_name = (await match_teams_names[1].text_content()).strip()

                    result.append(
                        MatchInfo(
                            url="https://betcity.ru" + match_url,
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
                
            except PlaywrightTimeoutError as ex:
                logger.warning(f"Attempt {attempt + 1} failed for league {league_name}: {str(ex)}")
                if attempt < self._max_retries - 1:
                    logger.info(f"Retrying in {self._retry_delay} seconds...")
                    await asyncio.sleep(self._retry_delay)
                else:
                    logger.error(f"All {self._max_retries} attempts failed for league {league_name}")
            except Exception as ex:
                logger.exception("An unexpected error while parsing betcity league matches")
                break
            finally:
                if context is not None:
                    await context.close()
                if browser is not None:
                    await browser.close()

        return result

    @staticmethod
    def _add_both_scores_value(match_info: MatchInfo, type: str, value: float) -> MatchInfo:
        if type == "Да":
            match_info.both_score_yes = value
        elif type == "Нет":
            match_info.both_score_no = value
        return match_info
    
    def _parse_both_scores_bets(self, bet_group: Any, match_info: MatchInfo) -> MatchInfo:
        group_blocks = bet_group.find_all(class_="dops-item-row__block")
        if len(group_blocks) != 2:
            return match_info

        type_1_elem = group_blocks[0].find(class_="dops-item-row__block-left")
        value_1_elem = group_blocks[0].find(class_="dops-item-row__block-right")
        type_2_elem = group_blocks[1].find(class_="dops-item-row__block-left")
        value_2_elem = group_blocks[1].find(class_="dops-item-row__block-right")

        if type_1_elem is None or value_1_elem is None or type_2_elem is None or value_2_elem is None:
            return match_info

        type_1 = type_1_elem.text.strip()
        value_1 = float(value_1_elem.text.strip())
        type_2 = type_2_elem.text.strip()
        value_2 = float(value_2_elem.text.strip())

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
        group_rows = bet_group.find_all(class_="dops-item-row__section")
        for group_row in group_rows:
            row_blocks = group_row.find_all(class_="dops-item-row__block")

            if len(row_blocks) < 2:
                continue

            base = row_blocks[0].text.strip()
            for row_block in row_blocks[1:]:
                type_elem = row_block.find(class_="dops-item-row__block-left")
                value_elem = row_block.find(class_="dops-item-row__block-right")

                if type_elem is None or value_elem is None:
                    continue

                type = type_elem.text.strip()
                value = float(value_elem.text.strip())
                match_info = self._add_total_bet_value(match_info, base, type, value)

        return match_info

    @staticmethod
    def _parse_handicap_base_type(base_type: str) -> Tuple[str, str]:
        base, type = base_type.split()
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
        group_rows = bet_group.find_all(class_="dops-item-row__section")
        for group_row in group_rows:
            row_blocks = group_row.find_all(class_="dops-item-row__block")

            if len(row_blocks) == 0:
                continue

            for row_block in row_blocks:
                base_type_elem = row_block.find(class_="dops-item-row__block-left")
                value_elem = row_block.find(class_="dops-item-row__block-right")

                if base_type_elem is None or value_elem is None:
                    continue

                base_type = base_type_elem.text.strip()
                value = float(value_elem.text.strip())

                base, type = self._parse_handicap_base_type(base_type)
                match_info = self._add_handicap_bet_value(match_info, base, type, value)

        return match_info

    @staticmethod
    def _parse_individual_total_base_type(base_type: str) -> Tuple[str, str]:
        base, type = base_type.split()
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
        group_rows = bet_group.find_all(class_="dops-item-row__section")
        for group_row in group_rows:
            row_blocks = group_row.find_all(class_="dops-item-row__block")

            if len(row_blocks) < 2:
                continue

            base_type = row_blocks[0].text.strip()

            base, type = self._parse_handicap_base_type(base_type)
            for row_block in row_blocks[1:]:
                subtype_elem = row_block.find(class_="dops-item-row__block-left")
                value_elem = row_block.find(class_="dops-item-row__block-right")

                if subtype_elem is None or value_elem is None:
                    continue

                subtype = subtype_elem.text.strip()
                value = float(value_elem.text.strip())
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
        group_rows = bet_group.find_all(class_="dops-item-row__section")
        for group_row in group_rows:
            row_blocks = group_row.find_all(class_="dops-item-row__block")

            if len(row_blocks) < 2:
                continue

            base = row_blocks[0].text.strip()
            for row_block in row_blocks[1:]:
                type_elem = row_block.find(class_="dops-item-row__block-left")
                value_elem = row_block.find(class_="dops-item-row__block-right")

                if type_elem is None or value_elem is None:
                    continue

                type = type_elem.text.strip()
                value = float(value_elem.text.strip())
                match_info = self._add_goals_bet_value(match_info, base, type, value)

        return match_info
    
    async def _parse_main_bets(self, page: Page, match_info: MatchInfo) -> MatchInfo:
        bet_groups = await page.wait_for_selector(".dops-item", timeout=3000)
        if bet_groups is None:
            logger.warning(f"Line header not found for match: {match_info.url}")
            return match_info

        page_content = await page.content()
        soup = BeautifulSoup(page_content, 'html.parser')
        all_bet_groups = soup.find_all(class_="dops-item")

        for bet_group in all_bet_groups:
            group_title_elem = bet_group.find(class_="dops-item__title")
            
            if group_title_elem is None:
                continue
            group_title = group_title_elem.text.strip()

            if group_title.lower() in self._bet_group_methods:
                match_info = self._bet_group_methods[group_title.lower()](bet_group, match_info)

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
        elif prev_title is not None and (prev_title == "ТОТ" or prev_title == "TOT"):
            if cur_title == "М" or cur_title == "M":
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
        elif prev_prev_title is not None and (prev_prev_title == "ТОТ" or prev_prev_title == "TOT"):
            if cur_title == "М" or cur_title == "M":
                match_info = BetcityParser._add_total_bet_value(
                    match_info=match_info, 
                    base=prev_prev_value, 
                    type="Мен", 
                    value=float(cur_value)
                )
            elif cur_title == "Б":
                match_info = BetcityParser._add_total_bet_value(
                    match_info=match_info, 
                    base=prev_prev_value, 
                    type="Бол", 
                    value=float(cur_value)
                )
        return match_info
    
    def _parse_header_bets_titles(self, line_header: Any) -> List[str]:
        header_items = line_header.find_all("span", {"class": "line__header-item_dop"})
        result = []
        for header_item in header_items:
            result.append(header_item.text.strip())
        return result

    def _parse_header_bets_values(self, main_bets: Any) -> List[str]:
        bets_buttons = main_bets.find_all(class_="line-event__main-bets-button")
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

    async def _parse_header_bets(self, page: Page, match_info: MatchInfo) -> MatchInfo:
        try:
            await page.wait_for_load_state('networkidle', timeout=30000)
            
            line_header = await page.wait_for_selector(".line__header", timeout=3000)
            if line_header is None:
                logger.warning(f"Line header not found for match: {match_info.url}")
                return match_info
            main_bets = await page.wait_for_selector(".line-event__main-bets", timeout=3000)
            if main_bets is None:
                logger.warning(f"Main bets not found for match: {match_info.url}")
                return match_info

            page_content = await page.content()
            soup = BeautifulSoup(page_content, 'html.parser')

            line_header = soup.find("div", {"class": "line__header"})
            main_bets = soup.find("div", {"class": "line-event__main-bets"})
            
            if line_header is None or main_bets is None:
                logger.warning(f"Line header or main bets not found for match: {match_info.url}")
                return match_info

            bets_titles = self._parse_header_bets_titles(line_header)
            bets_values = self._parse_header_bets_values(main_bets)
            match_info = self._merge_header_bets(bets_titles, bets_values, match_info)
        except Exception as e:
            logger.exception(f"Error in _parse_header_bets for match: {match_info.url}: {e}")

        return match_info

    async def _parse_match(self, match_info: MatchInfo) -> MatchInfo:
        browser = None
        context = None
        use_proxy = True

        for attempt in range(self._max_retries):
            try:
                browser, context = await self._create_browser_context(use_proxy=use_proxy)
                page = await context.new_page()
                page.set_default_timeout(self._page_timeout * 1000)

                logger.info(f"Attempt {attempt + 1}: Parsing match {match_info.url} (proxy: {use_proxy})")
                
                response = await page.goto(match_info.url, wait_until='domcontentloaded', timeout=30000)
                await page.wait_for_timeout(3000)
                await page.wait_for_load_state('networkidle', timeout=30000)

                match_info = await self._parse_header_bets(page, match_info)
                match_info = await self._parse_main_bets(page, match_info)

                logger.info(f"Match {match_info.url} parsed successfully")
                break
            except PlaywrightTimeoutError as ex:
                logger.warning(f"Attempt {attempt + 1} failed for match {match_info.url}: {str(ex)}")
                if attempt < self._max_retries - 1:
                    logger.info(f"Retrying in {self._retry_delay} seconds...")
                    await asyncio.sleep(self._retry_delay)
                else:
                    logger.error(f"All {self._max_retries} attempts failed for match {match_info.url}")
            except Exception as ex:
                logger.exception("An unexpected error while parsing betcity match")
                break
            finally:
                if context is not None:
                    await context.close()
                if browser is not None:
                    await browser.close()

        return match_info

    async def get_league_matches(self, league_name: str) -> List[MatchInfo]:
        result = []
        logger.info(f"get betcity matches for {league_name}")
        league_matches = await self._parse_league_matches(league_name)
        if league_matches is not None:
            for match in league_matches:
                parsed_match = await self._parse_match(match)
                if (
                    parsed_match.total_1_over_1_5 is not None
                    or parsed_match.total_1_under_0_5 is not None
                    or parsed_match.total_2_over_1_5 is not None
                    or parsed_match.total_2_under_0_5 is not None
                ):
                    result.append(parsed_match)

        return result
