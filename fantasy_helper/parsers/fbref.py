import logging
import os
import sys
import typing as t

import requests
from bs4 import BeautifulSoup

from fantasy_helper.utils.dataclasses import LeagueInfo


class FbrefParser:
    def __init__(self, leagues: t.List[LeagueInfo]):
        self.__shoots_leagues = {
            l.name: l.fbref_shoots_url
            for l in leagues
            if l.fbref_shoots_url is not None
        }
        self.__xg_leagues = {
            l.name: l.fbref_xg_url for l in leagues if l.fbref_xg_url is not None
        }
        self.__shoots_creation_leagues = {
            l.name: l.fbref_shoots_creation_url
            for l in leagues
            if l.fbref_shoots_creation_url is not None
        }

    def get_shooting_stats(self, league_name: str) -> t.List[dict]:
        result: t.List[dict] = []
        try:
            if league_name not in self.__shoots_leagues:
                return result
            response = requests.get(self.__shoots_leagues[league_name])
            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table")
            players = table.find_all("tr")[2:]

            for cur_player in players:
                if cur_player.find("td", {"data-stat": "player"}) is not None:
                    _goals = cur_player.find("td", {"data-stat": "goals"}).text
                    _minutes = cur_player.find("td", {"data-stat": "minutes_90s"}).text
                    _shots_total = cur_player.find(
                        "td", {"data-stat": "shots_total"}
                    ).text
                    _shots_target = cur_player.find(
                        "td", {"data-stat": "shots_total"}
                    ).text
                    result.append(
                        {
                            "league": league_name,
                            "name": cur_player.find("td", {"data-stat": "player"}).text,
                            "team": cur_player.find("td", {"data-stat": "squad"}).text,
                            "position": cur_player.find(
                                "td", {"data-stat": "position"}
                            ).text,
                            "goals": int(_goals) if _goals else 0,
                            "minutes": float(_minutes) if _minutes else 0.0,
                            "shots_total": int(_shots_total) if _shots_total else 0.0,
                            "shots_on_target": int(_shots_target)
                            if _shots_target
                            else 0.0,
                        }
                    )
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            return result

    def get_xg_stats(self, league_name: str) -> t.List[dict]:
        result: t.List[dict] = []
        try:
            if league_name not in self.__xg_leagues:
                return result
            response = requests.get(self.__xg_leagues[league_name])
            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table")
            players = table.find_all("tr")[2:]

            for cur_player in players:
                if cur_player.find("td", {"data-stat": "player"}) is not None:
                    _xg = cur_player.find("td", {"data-stat": "xg"}).text
                    _npxg = cur_player.find("td", {"data-stat": "npxg"}).text
                    _xa = cur_player.find("td", {"data-stat": "xa"}).text
                    result.append(
                        {
                            "league": league_name,
                            "name": cur_player.find("td", {"data-stat": "player"}).text,
                            "team": cur_player.find("td", {"data-stat": "squad"}).text,
                            "position": cur_player.find(
                                "td", {"data-stat": "position"}
                            ).text,
                            "xg": float(_xg) if _xg else 0.0,
                            "npxg": float(_npxg) if _npxg else 0.0,
                            "xa": float(_xa) if _xa else 0.0,
                        }
                    )
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            return result

    def get_shoot_creation_stats(self, league_name: str) -> t.List[dict]:
        result: t.List[dict] = []
        try:
            if league_name not in self.__shoots_creation_leagues:
                return result
            response = requests.get(self.__shoots_creation_leagues[league_name])
            soup = BeautifulSoup(response.text, "lxml")
            table = soup.find("table")
            players = table.find_all("tr")[2:]

            for cur_player in players:
                if cur_player.find("td", {"data-stat": "player"}) is not None:
                    _sca = cur_player.find("td", {"data-stat": "sca"}).text
                    _gca = cur_player.find("td", {"data-stat": "gca"}).text
                    result.append(
                        {
                            "league": league_name,
                            "name": cur_player.find("td", {"data-stat": "player"}).text,
                            "team": cur_player.find("td", {"data-stat": "squad"}).text,
                            "position": cur_player.find(
                                "td", {"data-stat": "position"}
                            ).text,
                            "sca": int(_sca) if _sca else 0,
                            "gca": int(_gca) if _gca else 0,
                        }
                    )
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            return result
