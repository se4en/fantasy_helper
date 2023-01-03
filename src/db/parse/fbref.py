import logging
from typing import Tuple, List, Dict
import requests
import os
import sys
from bs4 import BeautifulSoup
from datetime import datetime


class FbrefParser:

    def __init__(self):
        self.shoots_leagues = {
            'Russia': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F30%2Fshooting%2FRussian-Premier-League-Stats&div=div_stats_shooting',
            'France': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F13%2Fshooting%2FLigue-1-Stats&div=div_stats_shooting',
            'England': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F9%2Fshooting%2FPremier-League-Stats&div=div_stats_shooting',
            'Germany': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F20%2Fshooting%2FBundesliga-Stats&div=div_stats_shooting',
            'Spain': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F12%2Fshooting%2FLa-Liga-Stats&div=div_stats_shooting',
            'Netherlands': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F23%2Fshooting%2FEredivisie-Stats&div=div_stats_shooting',
            'Turkey': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F26%2Fshooting%2FSuper-Lig-Stats&div=div_stats_shooting',
            'Italy': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F11%2Fshooting%2FSerie-A-Stats&div=div_stats_shooting',
            'Portugal': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F32%2Fshooting%2FPrimeira-Liga-Stats&div=div_stats_shooting',
            # 'UEFA_1': 'https://fbref.com/en/comps/8/Champions-League-Stats',
            # 'UEFA_2': 'https://fbref.com/en/comps/19/Europa-League-Stats',
        }

        self.xg_leagues = {
            'France': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F13%2Fstats%2FLigue-1-Stats&div=div_stats_standard',
            'England': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F9%2Fstats%2FPremier-League-Stats&div=div_stats_standard',
            'Germany': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F20%2Fstats%2FBundesliga-Stats&div=div_stats_standard',
            'Spain': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F12%2Fstats%2FLa-Liga-Stats&div=div_stats_standard',
            'Italy': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F11%2Fstats%2FSerie-A-Stats&div=div_stats_standard',
        }

        self.shoots_creation_leagues = {
            'France': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F13%2Fgca%2FLigue-1-Stats&div=div_stats_gca',
            'England': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F9%2Fgca%2FPremier-League-Stats&div=div_stats_gca',
            'Germany': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F20%2Fgca%2FBundesliga-Stats&div=div_stats_gca',
            'Spain': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F12%2Fgca%2FLa-Liga-Stats&div=div_stats_gca',
            'Italy': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F11%2Fgca%2FSerie-A-Stats&div=div_stats_gca',
        }

    def get_shooting_stats(self, league_name: str) -> List[Dict]:
        logging.info(f"Get shoots stats in league={league_name}")
        result = []
        try:
            if league_name not in self.shoots_leagues:
                return result
            response = requests.get(self.shoots_leagues[league_name])
            soup = BeautifulSoup(response.text, 'lxml')
            table = soup.find("table")
            players = table.find_all("tr")[2:]

            for cur_player in players:
                if cur_player.find("td", {"data-stat": "player"}) is not None:
                    _goals = cur_player.find("td", {"data-stat": "goals"}).text
                    _minutes = cur_player.find("td", {"data-stat": "minutes_90s"}).text
                    _shots_total = cur_player.find("td", {"data-stat": "shots_total"}).text
                    _shots_target = cur_player.find("td", {"data-stat": "shots_total"}).text
                    result.append({
                        "league": league_name,
                        "name": cur_player.find("td", {"data-stat": "player"}).text,
                        "team": cur_player.find("td", {"data-stat": "squad"}).text,
                        "position": cur_player.find("td", {"data-stat": "position"}).text,
                        "goals": int(_goals) if _goals else 0,
                        "minutes": float(_minutes) if _minutes else 0.0,
                        "shots_total": int(_shots_total) if _shots_total else 0.0,
                        "shots_on_target": int(_shots_target) if _shots_target else 0.0
                    })
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            return result

    def get_xg_stats(self, league_name: str) -> List[Dict]:
        logging.info(f"Get xg stats in league={league_name}")
        result = []
        try:
            if league_name not in self.xg_leagues:
                return result
            response = requests.get(self.xg_leagues[league_name])
            soup = BeautifulSoup(response.text, 'lxml')
            table = soup.find("table")
            players = table.find_all("tr")[2:]

            for cur_player in players:
                if cur_player.find("td", {"data-stat": "player"}) is not None:
                    _xg = cur_player.find("td", {"data-stat": "xg"}).text
                    _npxg = cur_player.find("td", {"data-stat": "npxg"}).text
                    _xa = cur_player.find("td", {"data-stat": "xa"}).text
                    result.append({
                        "league": league_name,
                        "name": cur_player.find("td", {"data-stat": "player"}).text,
                        "team": cur_player.find("td", {"data-stat": "squad"}).text,
                        "position": cur_player.find("td", {"data-stat": "position"}).text,
                        "xg": float(_xg) if _xg else 0.0,
                        "npxg": float(_npxg) if _npxg else 0.0,
                        "xa": float(_xa) if _xa else 0.0,
                    })
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            return result

    def get_shoot_creation_stats(self, league_name: str) -> List[Dict]:
        logging.info(f"Get shoot creation stats in league={league_name}")
        result = []
        try:
            if league_name not in self.shoots_creation_leagues:
                return result
            response = requests.get(self.shoots_creation_leagues[league_name])
            soup = BeautifulSoup(response.text, 'lxml')
            table = soup.find("table")
            players = table.find_all("tr")[2:]

            for cur_player in players:
                if cur_player.find("td", {"data-stat": "player"}) is not None:
                    _sca = cur_player.find("td", {"data-stat": "sca"}).text
                    _gca = cur_player.find("td", {"data-stat": "gca"}).text
                    result.append({
                        "league": league_name,
                        "name": cur_player.find("td", {"data-stat": "player"}).text,
                        "team": cur_player.find("td", {"data-stat": "squad"}).text,
                        "position": cur_player.find("td", {"data-stat": "position"}).text,
                        "sca": int(_sca) if _sca else 0,
                        "gca": int(_gca) if _gca else 0,
                    })
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            return result


# if __name__ == "__main__":
#     fbref = FbrefParser()
#     res = fbref.get_shoot_creation_stats("France")
#     for _ in res:
#         print(_)
