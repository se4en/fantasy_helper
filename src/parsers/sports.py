from time import sleep
from typing import Optional, Tuple, List, Dict

# import requests
import os
import sys
from datetime import datetime
import logging


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Sports:
    def __init__(
        self,
        leagues: Optional[Dict[str, str]] = None,
        leagues_teams: Optional[Dict[str, str]] = None,
        delay: int = 3,
    ):
        self._delay = delay
        if leagues is not None:
            self.leagues = leagues
        else:
            self.leagues = {
                # 'Russia': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/31.html',
                # 'France': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/51.html',
                # 'England': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/52.html',
                # 'Germany': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/50.html',
                # 'Spain': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/49.html',
                # 'Netherlands': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/54.html',
                # 'Championship': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/205.html',
                # 'Turkey': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/246.html',
                # 'Italy': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/48.html',
                # 'Portugal': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/207.html',
                # 'UEFA_1': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/57.html',
                # 'UEFA_2': 'https://www.sports.ru/fantasy/football/tournament/ratings/popular/56.html',
            }

        if leagues_teams is not None:
            self._leagues_teams = leagues_teams
        else:
            self._leagues_teams = {
                "Russia": "https://www.sports.ru/fantasy/football/russia/2517/",
                "England": "https://www.sports.ru/fantasy/football/championship/20246/",
                "France": "https://www.sports.ru/fantasy/football/france/37361/",
                "Germany": "https://www.sports.ru/fantasy/football/germany/25743/",
                "Spain": "https://www.sports.ru/fantasy/football/spain/54224/",
                "Netherlands": "https://www.sports.ru/fantasy/football/netherlands/37305/",
                "Championship": "https://www.sports.ru/fantasy/football/championship/20246/",
                "Turkey": "https://www.sports.ru/fantasy/football/turkey/37322/",
                "Italy": "https://www.sports.ru/fantasy/football/italy/54230/",
                "Portugal": "https://www.sports.ru/fantasy/football/portugal/37317/",
                # "UEFA_1": "https://www.sports.ru/fantasy/football/team/points/2341584.html",
                # "UEFA_2": "https://www.sports.ru/fantasy/football/team/points/2344140.html",
            }

    def __transform_deadline(self, deadline: str) -> datetime:
        day, month_time = deadline.split(" ")
        month, time = month_time.split("|")

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
            "декабря": 12,
        }[month]
        hour, minute = list(map(int, time.split(":")))
        return datetime(datetime.now().year, month, day, hour, minute)

    def get_deadline(self, league_name: str) -> datetime:
        if league_name not in self._leagues_teams:
            logging.info(f"Wrong league_name={league_name} in get_deadline")
            return None
        try:
            response = requests.get(self._leagues_teams[league_name])
            soup = BeautifulSoup(response.text, "lxml")

            deadline = (
                soup.find("div", {"class": "team-info-block"})
                .find_all("tr")[1]
                .find("td")
                .text
            )
            return self.__transform_deadline(deadline)
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return None

    def get_games_count(self, league_name: str) -> int:
        if league_name not in self._leagues_teams:
            return -1
        try:
            driver = webdriver.Firefox()
            driver.get(self._leagues_teams[league_name])

            all_matches = WebDriverWait(driver, self._delay).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//div[@class='fantasy-match-list__matches']",
                    )
                )
            )

            result = len(
                all_matches.find_elements(
                    By.XPATH,
                    "//div[@class='fantasy-match-item']",
                )
            )
            return result
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return -1
        finally:
            if driver is not None:
                driver.close()

        # elem = driver.find_element(By.NAME, "q")
        # elem.clear()
        # elem.send_keys("pycon")
        # elem.send_keys(Keys.RETURN)
        # assert "No results found." not in driver.page_source
        # driver.close()

        # response = requests.get(self._leagues_teams[league_name])
        # soup = BeautifulSoup(response.text, "lxml")

        # matches_list = soup.find("div", {"class": "fantasy-match-list__matches"})
        # print(matches_list)
        # return len(matches_list.find_all("div", {"class": "fantasy-match-item"}))

    def __get_players_from_page(self, league_name: str, page_num: int) -> List[Dict]:
        result = []
        try:
            page_url = self.leagues[league_name] + f"?p={page_num + 1}"
            response = requests.get(page_url)
            soup = BeautifulSoup(response.text, "lxml")
            players = soup.find_all("tr")

            for i in range(len(players) - 1):
                player_population = int(players[i + 1].find_all("td")[-1].text)
                player_info = (
                    players[i + 1].find("div", {"class": "overBox"}).text.split("\n")
                )
                player_name = player_info[1]
                player_amplua = player_info[2]
                player_team = player_info[3]
                result.append(
                    {
                        "name": player_name,
                        "league": league_name,
                        "team": player_team,
                        "amplua": player_amplua,
                        "popularity": player_population,
                    }
                )
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


if __name__ == "__main__":
    sports = Sports()
    # print(sports.get_deadline("Russia"))
    print(sports.get_games_count("Russia"))

    # for player in sports.get_league_players("Russia"):
    #     print(player)
