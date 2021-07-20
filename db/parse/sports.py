import requests
from bs4 import BeautifulSoup
from datetime import datetime


class Sports:

    def __init__(self, leagues: dict = None, leagues_teams: dict = None):
        if leagues:
            self._leagues = leagues
            return
        else:
            self._leagues = {
                'Russia', 'https://www.sports.ru/fantasy/football/tournament/31.html',
                'France', 'https://www.sports.ru/fantasy/football/tournament/51.html',
                'England', 'https://www.sports.ru/fantasy/football/tournament/52.html',
                'Germany', 'https://www.sports.ru/fantasy/football/tournament/50.html',
                'Spain', 'https://www.sports.ru/fantasy/football/tournament/49.html',
                'Netherlands', 'https://www.sports.ru/fantasy/football/tournament/54.html',
                'Championship', 'https://www.sports.ru/fantasy/football/tournament/205.html',
                'Turkey', 'https://www.sports.ru/fantasy/football/tournament/246.html',
                'Italy', 'https://www.sports.ru/fantasy/football/tournament/48.html',
                'Portugal', 'https://www.sports.ru/fantasy/football/tournament/207.html',
                'UEFA_1', 'https://www.sports.ru/fantasy/football/tournament/57.html',
                'UEFA_2', 'https://www.sports.ru/fantasy/football/tournament/56.html',
            }

        if leagues_teams is not None:
            self._leagues_teams = leagues_teams
            return
        self._leagues_teams = {
            'Russia': 'https://www.sports.ru/fantasy/football/team/points/2301672.html',  # ok
            'England': 'https://www.sports.ru/fantasy/football/team/points/2243551.html',
            'France': 'https://www.sports.ru/fantasy/football/team/points/2232514.html',
            'Germany': 'https://www.sports.ru/fantasy/football/team/points/2243555.html',
            'Spain': 'https://www.sports.ru/fantasy/football/team/points/2243562.html',
            'Netherlands': 'https://www.sports.ru/fantasy/football/team/points/2243575.html',
            'Championship': 'https://www.sports.ru/fantasy/football/team/points/2243558.html',
            'Turkey': 'https://www.sports.ru/fantasy/football/team/points/2243571.html',
            'Italy': 'https://www.sports.ru/fantasy/football/team/points/2258596.html',
            'Portugal': 'https://www.sports.ru/fantasy/football/team/points/2258098.html',
            'UEFA_1': 'https://www.sports.ru/fantasy/football/team/points/2283074.html',
            'UEFA_2': 'https://www.sports.ru/fantasy/football/team/points/2284228.html',
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
            return None
        try:
            response = requests.get(self._leagues_teams[league_name])
            soup = BeautifulSoup(response.text, 'lxml')

            deadline = soup.find("div", {"class": "team-info-block"}).find_all("tr")[1] \
                .find("td").text
            return self._transform_deadline(deadline)
        except Exception as ex:
            # logs here
            print("Caught it!", ex)
            return None

    def get_games_count(self, league_name: str) -> int:
        if league_name not in self._leagues_teams:
            return None
        try:
            response = requests.get(self._leagues_teams[league_name])
            soup = BeautifulSoup(response.text, 'lxml')

            buf = soup.find("div", {"class": "mainPart points-page"}).find("div", {"class": "stat mB20"})
            return len(buf.find("table").find("tbody").find_all("tr"))
        except Exception as ex:
            # logs here
            print("Caught it!", ex)
            return None


if __name__ == "__main__":
    sports = Sports()
    print(sports.get_deadline("Russia"))
    print(sports.get_games_count("Russia"))
