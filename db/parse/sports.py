from typing import Tuple, List, Dict
import requests
import os
import sys
from bs4 import BeautifulSoup
from datetime import datetime
import logging


class Sports:

    def __init__(self, leagues: dict = None, leagues_teams: dict = None):
        if leagues:
            self.leagues = leagues
            return
        else:
            self.leagues = {
                'Russia': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/31.html',
                'France': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/51.html',
                'England': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/50.html',
                'Germany': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/50.html',
                # 'Spain': 'https://www.sports.ru/fantasy/football/tournament/49.html',
                # 'Netherlands': 'https://www.sports.ru/fantasy/football/tournament/54.html',
                'Championship': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/205.html',
                # 'Turkey': 'https://www.sports.ru/fantasy/football/tournament/246.html',
                # 'Italy': 'https://www.sports.ru/fantasy/football/tournament/48.html',
                'Portugal': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/207.html',
                # 'UEFA_1': 'https://www.sports.ru/fantasy/football/tournament/57.html',
                # 'UEFA_2': 'https://www.sports.ru/fantasy/football/tournament/56.html',
            }

        if leagues_teams is not None:
            self._leagues_teams = leagues_teams
            return
        self._leagues_teams = {
            'Russia': 'https://www.sports.ru/fantasy/football/team/points/2301672.html',  # ok
            'England': 'https://www.sports.ru/fantasy/football/team/points/2316271.html',  # ok
            'France': 'https://www.sports.ru/fantasy/football/team/points/2311561.html',  # ok
            'Germany': 'https://www.sports.ru/fantasy/football/team/points/2312024.html',  # ok
            # 'Spain': 'https://www.sports.ru/fantasy/football/team/points/2243562.html',
            # 'Netherlands': 'https://www.sports.ru/fantasy/football/team/points/2243575.html',
            'Championship': 'https://www.sports.ru/fantasy/football/team/points/2314647.html',  # ok
            # 'Turkey': 'https://www.sports.ru/fantasy/football/team/points/2243571.html',
            # 'Italy': 'https://www.sports.ru/fantasy/football/team/points/2258596.html',
            'Portugal': 'https://www.sports.ru/fantasy/football/team/points/2314643.html',  # ok
            # 'UEFA_1': 'https://www.sports.ru/fantasy/football/team/points/2283074.html',
            # 'UEFA_2': 'https://www.sports.ru/fantasy/football/team/points/2284228.html',
        }

    def __transform_deadline(self, deadline: str) -> datetime:
        day, month_time = deadline.split(' ')
        month, time = month_time.split('|')

        day = int(day)
        month = {
            "января": 1,
            "февраля": 2,
            "марта": 3,
            "апреля": 4,
            "мая": 5,
            "июня": 6,
            "июля": 7,
            "августа": 8,
            "сентября": 9,
            "октября": 10,
            "ноября": 11,
            "декабря": 12
        }[month]
        hour, minute = list(map(int, time.split(":")))
        return datetime(datetime.now().year, month, day, hour, minute)

    def get_deadline(self, league_name: str) -> datetime:
        if league_name not in self._leagues_teams:
            logging.info(f"Wrong league_name={league_name} in get_deadline")
            return None
        try:
            response = requests.get(self._leagues_teams[league_name])
            soup = BeautifulSoup(response.text, 'lxml')

            deadline = soup.find("div", {"class": "team-info-block"}).find_all("tr")[1] \
                .find("td").text
            return self.__transform_deadline(deadline)
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return None

    def get_games_count(self, league_name: str) -> int:
        if league_name not in self._leagues_teams:
            return 0
        try:
            response = requests.get(self._leagues_teams[league_name])
            soup = BeautifulSoup(response.text, 'lxml')

            buf = soup.find("div", {"class": "mainPart points-page"}).find("div", {"class": "stat mB20"})
            return len(buf.find("table").find("tbody").find_all("tr"))
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return 0

    def __get_players_from_page(self, league_name: str, page_num: int) -> List[Dict]:
        result = []
        try:
            page_url = self.leagues[league_name] + f"?p={page_num + 1}"
            response = requests.get(page_url)
            soup = BeautifulSoup(response.text, 'lxml')
            players = soup.find_all("tr")

            for i in range(len(players) - 1):
                player_population = int(players[i+1].find_all("td")[-1].text)
                player_info = players[i+1].find("div", {"class": "overBox"}).text.split("\n")
                player_name = player_info[1]
                player_amplua = player_info[2]
                player_team = player_info[3]
                result.append({
                    "name": player_name, "league": league_name, "team": player_team,
                    "amplua": player_amplua, "popularity": player_population
                })
            return result
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return result

    def get_league_players(self, league_name: str) -> List[Dict]:
        result = []
        if league_name not in self.leagues:
            return result
        i = 0
        page_result = self.__get_players_from_page(league_name, i)
        while page_result:
            result += page_result
            i += 1
            page_result = self.__get_players_from_page(league_name, i)
        return result


# if __name__ == "__main__":
#     sports = Sports()
#     #print(sports.get_deadline("Russia"))
#     #print(sports.get_games_count("Russia"))
#     for player in sports.get_league_players("Russia"):
#         print(player)
