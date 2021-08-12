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
            # 'England': 'https://fbref.com/en/comps/9/Premier-League-Stats',
            # 'Germany': 'https://fbref.com/en/comps/20/Bundesliga-Stats',
            # 'Spain': 'https://fbref.com/en/comps/12/La-Liga-Stats',
            # 'Netherlands': 'https://fbref.com/en/comps/23/Dutch-Eredivisie-Stats',
            # 'Turkey': 'https://fbref.com/en/comps/26/Super-Lig-Stats',
            # 'Italy': 'https://fbref.com/en/comps/11/Serie-A-Stats',
            'Portugal': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F32%2Fshooting%2FPrimeira-Liga-Stats&div=div_stats_shooting',
            # 'UEFA_1': 'https://fbref.com/en/comps/8/Champions-League-Stats',
            # 'UEFA_2': 'https://fbref.com/en/comps/19/Europa-League-Stats',
        }

        self.xg_leagues = {
            'France': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F13%2Fstats%2FLigue-1-Stats&div=div_stats_standard',
        }

        self.shoots_creation_leagues = {
            'France': 'https://widgets.sports-reference.com/wg.fcgi?css=1&site=fb&url=%2Fen%2Fcomps%2F13%2Fgca%2FLigue-1-Stats&div=div_stats_gca',
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
                    result.append({
                        "league": league_name,
                        "name": cur_player.find("td", {"data-stat": "player"}).text,
                        "team": cur_player.find("td", {"data-stat": "squad"}).text,
                        "position": cur_player.find("td", {"data-stat": "position"}).text,
                        "goals": int(cur_player.find("td", {"data-stat": "goals"}).text),
                        "minutes": float(cur_player.find("td", {"data-stat": "minutes_90s"}).text),
                        "shots_total": int(cur_player.find("td", {"data-stat": "shots_total"}).text),
                        "shots_on_target": int(cur_player.find("td", {"data-stat": "shots_on_target"}).text)
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
                    result.append({
                        "league": league_name,
                        "name": cur_player.find("td", {"data-stat": "player"}).text,
                        "team": cur_player.find("td", {"data-stat": "squad"}).text,
                        "position": cur_player.find("td", {"data-stat": "position"}).text,
                        "xg": float(cur_player.find("td", {"data-stat": "xg"}).text),
                        "npxg": float(cur_player.find("td", {"data-stat": "npxg"}).text),
                        "xa": float(cur_player.find("td", {"data-stat": "xa"}).text),
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
                    result.append({
                        "league": league_name,
                        "name": cur_player.find("td", {"data-stat": "player"}).text,
                        "team": cur_player.find("td", {"data-stat": "squad"}).text,
                        "position": cur_player.find("td", {"data-stat": "position"}).text,
                        "sca": int(cur_player.find("td", {"data-stat": "sca"}).text),
                        "gca": int(cur_player.find("td", {"data-stat": "gca"}).text),
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
