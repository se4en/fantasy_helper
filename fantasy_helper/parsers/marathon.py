import asyncio
from typing import List, Optional

from loguru import logger
from playwright.async_api import async_playwright

from fantasy_helper.conf.config import PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASSWORD
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


class MarathonParser:
    def __init__(self, leagues: List[LeagueInfo]):
        self._leagues = {
            l.name: l.marathon_url
            for l in leagues
            if l.marathon_url is not None and l.is_active
        }

    async def _parse_league_matches(self, league_name: str) -> Optional[List[MatchInfo]]:
        if league_name not in self._leagues:
            return None

        result = []
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
                proxy={
                    'server': f'http://{PROXY_HOST}:{PROXY_PORT}',
                    'username': PROXY_USER,
                    'password': PROXY_PASSWORD
                } if PROXY_HOST else None
            )
            
            page = await context.new_page()
            await page.goto(self._leagues[league_name], wait_until="networkidle")
            
            try:
                await page.wait_for_selector("div.bg.coupon-row", timeout=10000)
                match_rows = await page.query_selector_all("div.bg.coupon-row")
                
                if not match_rows:
                    logger.warning(f"No matches found for league {league_name}")
                    return []
                
                for row in match_rows:
                    try:
                        # Get team names from the member-area td
                        member_area = await row.query_selector("td.member-area")
                        if not member_area:
                            continue
                            
                        # Look for team links in the player rows
                        home_team_elem = await member_area.query_selector("div.player-row.player1 .member-name a")
                        away_team_elem = await member_area.query_selector("div.player-row.player2 .member-name a")
                        if not home_team_elem or not away_team_elem:
                            continue
                            
                        home_team = await home_team_elem.inner_text()
                        away_team = await away_team_elem.inner_text()
                        match_url = await home_team_elem.get_attribute("href")
                        
                        # Get odds from the price columns - look for the first 3 span.selection-link elements
                        odds_elements = await row.query_selector_all("td.price span.selection-link")
                        if len(odds_elements) < 3:
                            continue
                            
                        win1_text = await odds_elements[0].inner_text()
                        draw_text = await odds_elements[1].inner_text()
                        win2_text = await odds_elements[2].inner_text()
                        
                        match_info = MatchInfo(
                            url=f"https://www.marathonbet.com{match_url}" if match_url and not match_url.startswith('http') else match_url,
                            league_name=league_name,
                            home_team=home_team.strip(),
                            away_team=away_team.strip(),
                            win1=float(win1_text),
                            draw=float(draw_text),
                            win2=float(win2_text)
                        )
                        
                        result.append(match_info)
                    except Exception as e:
                        logger.exception(f"Failed to parse match: {e}")
                        continue
                
            except Exception as ex:
                logger.exception("Failed to parse league matches")
                return None
            finally:
                await browser.close()

        return result


    async def _parse_match(self, match_info: MatchInfo) -> MatchInfo:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36',
                proxy={
                    'server': f'http://{PROXY_HOST}:{PROXY_PORT}',
                    'username': PROXY_USER,
                    'password': PROXY_PASSWORD
                } if PROXY_HOST else None
            )
            
            page = await context.new_page()
            try:
                await page.goto(match_info.url, wait_until="networkidle")
                bet_groups = await page.query_selector_all(".dops-item")
                logging.debug(f"Found {len(bet_groups)} bet groups")
            finally:
                await browser.close()
                
        return match_info

    async def get_league_matches(self, league_name: str) -> List[MatchInfo]:
        league_matches = await self._parse_league_matches(league_name)
        if league_matches is not None:
            return league_matches
        return []
