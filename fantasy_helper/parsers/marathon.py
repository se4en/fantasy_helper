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
# from selenium.webdriver.firefox.options import Options

from fantasy_helper.conf.config import PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASSWORD
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


class MarathonParser:
    def __init__(self, leagues: List[LeagueInfo]):
        self._leagues = {
            l.name: l.marathon_url
            for l in leagues
            if l.marathon_url is not None and l.is_active
        }

    def _parse_league_matches(self, league_name: str) -> Optional[List[MatchInfo]]:
        if league_name not in self._leagues:
            return None

        print("PROXY", PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASSWORD)

        result = []
        driver = None
        try:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
            opts.add_argument("--disable-blink-features=AutomationControlled")

            # Configure proxy settings through Firefox preferences
            opts.set_preference("network.proxy.type", 1)  # Manual proxy configuration
            opts.set_preference("network.proxy.http", PROXY_HOST)
            opts.set_preference("network.proxy.http_port", int(PROXY_PORT))
            opts.set_preference("network.proxy.ssl", PROXY_HOST)
            opts.set_preference("network.proxy.ssl_port", int(PROXY_PORT))
            opts.set_preference("network.proxy.no_proxies_on", "localhost,127.0.0.1")

            # Add authentication for proxy
            # opts.set_preference("network.proxy.share_proxy_settings", True)

            # Create a profile with credentials for proxy authentication
            opts.set_preference("network.proxy.http.auth.user", PROXY_USER)
            opts.set_preference("network.proxy.http.auth.password", PROXY_PASSWORD)
            opts.set_preference("network.proxy.ssl.auth.user", PROXY_USER)
            opts.set_preference("network.proxy.ssl.auth.password", PROXY_PASSWORD)
                
                # Set auth prompt behavior
                # opts.set_preference("network.auth.subresource-http-auth-allow", 1)

            # Set connection timeouts
            opts.set_preference("network.http.connection-timeout", 10)  # 10 seconds
            opts.set_preference("network.http.response.timeout", 10)    # 10 seconds
            opts.set_preference("dom.max_script_run_time", 10)          # 10 seconds

            # Limit connection attempts
            opts.set_preference("network.http.max-connections", 48)
            opts.set_preference("network.http.max-connections-per-server", 16)

            # Disable unused features
            opts.set_preference("browser.cache.disk.enable", False)
            opts.set_preference("browser.cache.memory.enable", True)
            opts.set_preference("browser.cache.offline.enable", False)
            opts.set_preference("network.dns.disablePrefetch", True)
            opts.set_preference("network.prefetch-next", False)
            opts.set_preference("browser.tabs.remote.autostart", False)
            opts.set_preference("browser.tabs.remote.autostart.2", False)


            driver = webdriver.Firefox(
                executable_path=os.environ["GECKODRIVER_PATH"], options=opts
            )
            driver.get("https://httpbin.org/ip")
            print(driver.page_source)  # Should show the proxy's IP, not yours

            # driver.get(self._leagues[league_name])  

            # champ_line = WebDriverWait(driver, 3).until(
            #     EC.presence_of_element_located((By.CLASS_NAME, "foot-market"))
            # )

            # all_matches = champ_line.find_elements(By.CLASS_NAME, "bg coupon-row")
            # print("found matches", len(all_matches))




            # for match in all_matches:
            #     match_name_elem = match.find_element(By.CLASS_NAME, "line-event__name")
            #     match_url = match_name_elem.get_attribute("href")
            #     match_teams_names = match_name_elem.find_elements(By.TAG_NAME, "b")
            #     if len(match_teams_names) != 2:
            #         continue
            #     home_team_name = match_teams_names[0].text.strip()
            #     away_team_name = match_teams_names[1].text.strip()
            #     # team_names = match_url_elem.text.split("—")
            #     print(match_url, home_team_name, away_team_name)
            #     result.append(
            #         MatchInfo(
            #             url=match_url,
            #             league_name=league_name,
            #             home_team=match_teams_names[0].text.strip(),
            #             away_team=match_teams_names[1].text.strip(),
            #         )
            #     )
        # except Exception as ex:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     print(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            if driver is not None:
                driver.quit()

        return result


    def _parse_match(self, match_info: MatchInfo) -> MatchInfo:
        driver = None
        try:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
            opts.add_argument("--disable-blink-features=AutomationControlled")

            driver = webdriver.Firefox(
                executable_path=os.environ["GECKODRIVER_PATH"], options=opts
            )
            driver.get(match_info.url)

            bet_groups = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "dops-item"))
            )
            print("bet_groups", len(bet_groups))

        # except Exception as ex:
        #     exc_type, exc_obj, exc_tb = sys.exc_info()
        #     fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        #     print(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            if driver is not None:
                driver.quit()

        return match_info

    def get_league_matches(self, league_name: str) -> List[MatchInfo]:
        result = []
        league_matches = self._parse_league_matches(league_name)
        # if league_matches is not None:
        #     for match in league_matches:
        #         parsed_match = self._parse_match(match)
        #         if (
        #             parsed_match.total_1_over_1_5 is not None
        #             or parsed_match.total_1_under_0_5 is not None
        #             or parsed_match.total_2_over_1_5 is not None
        #             or parsed_match.total_2_under_0_5 is not None
        #         ):
        #             result.append(parsed_match)

        return result
