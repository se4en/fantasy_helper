import re
from typing import List

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


from fantasy_helper.utils.dataclasses import LeagueInfo, TeamLineup


class MoleParser:
    def __init__(self, leagues: List[LeagueInfo]):
        self._url = "https://www.sportsmole.co.uk/football/preview/"
        self._leagues = {
            l.sportsmole_name: l.name for l in leagues if l.sportsmole_name is not None and l.is_active
        }

        self._session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self._session.mount("http://", adapter)
        self._session.mount("https://", adapter)

    def _parse_lineups(self, url: str, league: str) -> List[TeamLineup]:
        try:
            response = self._session.get(url)
        except requests.exceptions.TooManyRedirects:
            # todo logging
            return []

        if response.status_code != 200:
            return []
        soup = BeautifulSoup(response.content, "html.parser")
        result = []

        pattern = r"([a-zA-Z \-\`\']+) possible starting lineup:([a-zA-Z ,;\-\`\']+)"
        matches = re.findall(pattern, soup.text)

        for team_name, team_lineup in matches:
            result.append(TeamLineup(team_name, league, team_lineup))

        return result

    def get_lineups(self) -> List[TeamLineup]:
        response = requests.get(self._url)
        soup = BeautifulSoup(response.content, "html.parser")
        found_leagues = soup.find_all(
            "div", class_="l_s_blocks_header l_s_blocks margin"
        )
        all_lineups = []

        for i in range(len(found_leagues)):
            start_tag = found_leagues[i]
            mole_league_name = start_tag.get_text("|").split("|")[0]
            if mole_league_name not in self._leagues:
                continue

            league_name = self._leagues[mole_league_name]

            current_tag = start_tag.find_next()
            while "l_s_blocks_header" not in current_tag.get("class", []):
                if current_tag.name == "a":
                    match_url = "https://www.sportsmole.co.uk" + current_tag.get("href")
                    match_lineups = self._parse_lineups(
                        url=match_url, league=league_name
                    )
                    all_lineups += match_lineups

                current_tag = current_tag.find_next()

        return all_lineups
