import re
from typing import List

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


from fantasy_helper.utils.dataclasses import LeagueInfo, TeamLineup


class MoleParser:
    def __init__(self, leagues: List[LeagueInfo]):
        self.__url = "https://www.sportsmole.co.uk/football/preview/"
        self.__leagues = {
            l.sportsmole_name: l.name for l in leagues if l.sportsmole_name is not None and l.is_active
        }

        self.__session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        self.__session.mount("http://", adapter)
        self.__session.mount("https://", adapter)

    def __parse_lineups(self, url: str, league: str) -> List[TeamLineup]:
        response = self.__session.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        result = []

        pattern = r"([a-zA-Z \-\`\']+) possible starting lineup:([a-zA-Z ,;\-\`\']+)"
        matches = re.findall(pattern, soup.text)

        for team_name, team_lineup in matches:
            result.append(TeamLineup(team_name, league, team_lineup))

        return result

    def get_lineups(self) -> List[TeamLineup]:
        response = requests.get(self.__url)
        soup = BeautifulSoup(response.content, "html.parser")
        found_leagues = soup.find_all(
            "div", class_="l_s_blocks_header l_s_blocks margin"
        )
        all_lineups = []

        for i in range(len(found_leagues)):
            start_tag = found_leagues[i]
            if i < len(found_leagues) - 1:
                end_tag = found_leagues[i + 1]
            else:
                end_tag = None
            mole_league_name = start_tag.get_text("|").split("|")[0]
            if mole_league_name not in self.__leagues:
                continue
            league_name = self.__leagues[mole_league_name]

            current_tag = start_tag
            while current_tag != end_tag:
                if current_tag.name == "a":
                    match_url = "https://www.sportsmole.co.uk" + current_tag.get("href")
                    match_lineups = self.__parse_lineups(
                        url=match_url, league=league_name
                    )
                    all_lineups += match_lineups

                current_tag = current_tag.find_next()

        return all_lineups
