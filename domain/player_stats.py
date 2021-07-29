import asyncio
import os
import sys
from datetime import datetime, timedelta
from typing import List
import pandas as pd
import numpy as np
import dataframe_image as dfi
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import bold, italic
from pandas.io.formats.style import Styler
from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession
from sqlalchemy.sql import label

from db.database import Session
from db.parse.fbref import FbrefParser
from domain.manager import Manager
from db.models.player_stats import PlayerStats
from db.utils.uploding_files import upload_files
from db.models.leagues_info import League_info


class PlayerStatsManager(Manager):

    def __init__(self, last3_minutes_min=1.0, last5_minutes_min=2.0, max_name_len=10, max_team_len=7):
        super().__init__()
        self.fbref = FbrefParser()
        self.LAST3_MIN = last3_minutes_min
        self.LAST5_MIN = last5_minutes_min
        self.MAX_NAME_LEN = max_name_len
        self.MAX_TEAM_LEN = max_team_len

    def get_player(self, player_info: dict) -> PlayerStats:
        session: SQLSession = Session()
        result = session.query(PlayerStats).filter(and_(PlayerStats.name == player_info['name'],
                                                        PlayerStats.league == player_info['league'],
                                                        PlayerStats.team == player_info['team'])).first()
        session.close()
        return result

    def __update_player(self, cur_player: PlayerStats) -> PlayerStats:
        """
        Update player stats for next round
        """
        session: SQLSession = Session()
        try:
            session.query(PlayerStats).filter(PlayerStats.id == cur_player.id).update({
                # round 0
                'r0_minutes': cur_player["r1_minutes"],
                'r0_shoots': cur_player["r1_shoots"],
                'r0_shoots_on_target': cur_player["r1_shoots_on_target"],
                'r0_xg': cur_player["r1_xg"],
                'r0_npxg': cur_player["r1_npxg"],
                'r0_xa': cur_player["r1_xa"],
                'r0_sca': cur_player["r1_sca"],
                'r0_gca': cur_player["r1_gca"],
                # round 1
                'r1_minutes': cur_player["r2_minutes"],
                'r1_shoots': cur_player["r2_shoots"],
                'r1_shoots_on_target': cur_player["r2_shoots_on_target"],
                'r1_xg': cur_player["r2_xg"],
                'r1_npxg': cur_player["r2_npxg"],
                'r1_xa': cur_player["r2_xa"],
                'r1_sca': cur_player["r2_sca"],
                'r1_gca': cur_player["r2_gca"],
                # round 2
                'r2_minutes': cur_player["r3_minutes"],
                'r2_shoots': cur_player["r3_shoots"],
                'r2_shoots_on_target': cur_player["r3_shoots_on_target"],
                'r2_xg': cur_player["r3_xg"],
                'r2_npxg': cur_player["r3_npxg"],
                'r2_xa': cur_player["r3_xa"],
                'r2_sca': cur_player["r3_sca"],
                'r2_gca': cur_player["r3_gca"],
                # round 3
                'r3_minutes': cur_player["r4_minutes"],
                'r3_shoots': cur_player["r4_shoots"],
                'r3_shoots_on_target': cur_player["r4_shoots_on_target"],
                'r3_xg': cur_player["r4_xg"],
                'r3_npxg': cur_player["r4_npxg"],
                'r3_xa': cur_player["r4_xa"],
                'r3_sca': cur_player["r4_sca"],
                'r3_gca': cur_player["r4_gca"],
                # round 4
                'r4_minutes': cur_player["r5_minutes"],
                'r4_shoots': cur_player["r5_shoots"],
                'r4_shoots_on_target': cur_player["r5_shoots_on_target"],
                'r4_xg': cur_player["r5_xg"],
                'r4_npxg': cur_player["r5_npxg"],
                'r4_xa': cur_player["r5_xa"],
                'r4_sca': cur_player["r5_sca"],
                'r4_gca': cur_player["r5_gca"],
            })
            upd_player = session.query(PlayerStats).filter(PlayerStats.id == cur_player.id).first()
            return upd_player
        except Exception as ex:
            # TODO logging
            print(ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return None
        finally:
            session.commit()
            session.close()

    def __compute_shoots(self, player_info: dict, player_stat: PlayerStats):
        last3_minutes = player_info["minutes"] - player_stat.r2_minutes
        last3_shoots = player_info["shots_total"] - player_stat.r2_shoots
        if last3_minutes < self.LAST3_MIN:
            last3_minutes = 0
            last3_shoots = 0
        last3_shoots_per_game = last3_shoots * last3_minutes
        if last3_shoots == 0:
            last3_on_target_per_shoot = 0
        else:
            last3_on_target_per_shoot = (player_info["shots_on_target"] -
                                         player_stat.r2_shoots_on_target) / last3_shoots

        last5_minutes = player_info["minutes"] - player_stat.r0_minutes
        last5_shoots = player_info["shots_total"] - player_stat.r0_shoots
        if last5_minutes < self.LAST5_MIN:
            last5_minutes = 0
            last5_shoots = 0
        last5_shoots_per_game = last5_shoots * last5_minutes
        if last5_shoots == 0:
            last5_on_target_per_shoot = 0
        else:
            last5_on_target_per_shoot = (player_info["shots_on_target"] -
                                         player_stat.r0_shoots_on_target) / last5_shoots

        return (last3_shoots_per_game, last3_on_target_per_shoot,
                last5_shoots_per_game, last5_on_target_per_shoot)

    def __update_shoots(self, league_name: str, new_round: bool = False) -> bool:
        session: SQLSession = Session()
        try:
            for player_stat in self.fbref.get_shooting_stats(league_name):
                cur_player: PlayerStats = self.get_player(player_stat)
                if cur_player:
                    if new_round:
                        cur_player = self.__update_player(cur_player)
                    last3_shoots_per_game, last3_on_target_per_shoot, last5_shoots_per_game, \
                    last5_on_target_per_shoot = self.__compute_shoots(player_stat, cur_player)

                    # if cur_player:
                    session.query(PlayerStats).filter(PlayerStats.id == cur_player.id).update({
                        'r5_minutes': player_stat["minutes"],
                        'r5_shoots': player_stat["shots_total"],
                        'r5_shoots_on_target': player_stat["shots_on_target"],
                        'last3_shoots_per_game': last3_shoots_per_game,
                        'last3_on_target_per_shoot': last3_on_target_per_shoot,
                        'last5_shoots_per_game': last5_shoots_per_game,
                        'last5_on_target_per_shoot': last5_on_target_per_shoot
                    })
                else:  # if new player
                    session.add(PlayerStats(player_stat['name'], league_name, player_stat['team'],
                                            player_stat['position']))
                    session.commit()
                    cur_player = self.get_player(player_stat)
                    if cur_player:
                        session.query(PlayerStats).filter(PlayerStats.id == cur_player.id).update({
                            'r5_minutes': player_stat["minutes"],
                            'r5_shoots': player_stat["shots_total"],
                            'r5_shoots_on_target': player_stat["shots_on_target"]
                        })
            return True
        except Exception as ex:
            # TODO logging
            print(ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return False
        finally:
            session.commit()
            session.close()

    def __compute_xg(self, player_info: dict, player_stat: PlayerStats):
        last3_minutes = player_info["minutes"] - player_stat.r2_minutes
        if last3_minutes < self.LAST3_MIN:
            last3_minutes = 0
        last3_xg_per_game = last3_minutes * (player_info["xg"] - player_stat.r2_xg)
        last3_npxg_per_game = last3_minutes * (player_info["npxg"] - player_stat.r2_npxg)
        last3_xa_per_game = last3_minutes * (player_info["xa"] - player_stat.r2_xa)

        last5_minutes = player_info["minutes"] - player_stat.r0_minutes
        if last5_minutes < self.LAST5_MIN:
            last5_minutes = 0
        last5_xg_per_game = last5_minutes * (player_info["xg"] - player_stat.r0_xg)
        last5_npxg_per_game = last5_minutes * (player_info["npxg"] - player_stat.r0_npxg)
        last5_xa_per_game = last5_minutes * (player_info["xa"] - player_stat.r0_xa)

        return (last3_xg_per_game, last3_npxg_per_game, last3_xa_per_game,
                last5_xg_per_game, last5_npxg_per_game, last5_xa_per_game)

    def __update_xg(self, league_name: str) -> bool:
        session: SQLSession = Session()
        try:
            for player_stat in self.fbref.get_xg_stats(league_name):
                cur_player: PlayerStats = self.get_player(player_stat)
                if cur_player:
                    last3_xg_per_game, last3_npxg_per_game, last3_xa_per_game, last5_xg_per_game, \
                    last5_npxg_per_game, last5_xa_per_game = self.__compute_xg(player_stat, cur_player)

                    session.query(PlayerStats).filter(PlayerStats.id == cur_player.id).update({
                        'r5_xg': player_stat["xg"],
                        'r5_npxg': player_stat["npxg"],
                        'r5_xa': player_stat["xa"],
                        'last3_xg_per_game': last3_xg_per_game,
                        'last3_npxg_per_game': last3_npxg_per_game,
                        'last3_xa_per_game': last3_xa_per_game,
                        'last5_xg_per_game': last5_xg_per_game,
                        'last5_npxg_per_game': last5_npxg_per_game,
                        'last5_xa_per_game': last5_xa_per_game
                    })
                else:  # if new player
                    session.add(PlayerStats(player_stat['name'], league_name, player_stat['team'],
                                            player_stat['position']))
                    session.commit()
                    cur_player = self.get_player(player_stat)
                    if cur_player:
                        session.query(PlayerStats).filter(PlayerStats.id == cur_player.id).update({
                            'r5_xg': player_stat["xg"],
                            'r5_npxg': player_stat["npxg"],
                            'r5_xa': player_stat["xa"]
                        })
            return True
        except Exception as ex:
            # TODO logging
            print(ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return False
        finally:
            session.commit()
            session.close()

    def __compute_shoots_creation(self, player_info: dict, player_stat: PlayerStats):
        last3_minutes = player_info["minutes"] - player_stat.r2_minutes
        if last3_minutes < self.LAST3_MIN:
            last3_minutes = 0
        last3_sca_per_game = last3_minutes * (player_info["sca"] - player_stat.r2_sca)
        last3_gca_per_game = last3_minutes * (player_info["gca"] - player_stat.r2_gca)

        last5_minutes = player_info["minutes"] - player_stat.r0_minutes
        if last5_minutes < self.LAST5_MIN:
            last5_minutes = 0
        last5_sca_per_game = last5_minutes * (player_info["sca"] - player_stat.r0_sca)
        last5_gca_per_game = last5_minutes * (player_info["gca"] - player_stat.r0_gca)

        return last3_sca_per_game, last3_gca_per_game, last5_sca_per_game, last5_gca_per_game

    def __update_shoots_creation(self, league_name: str) -> bool:
        session: SQLSession = Session()
        try:
            for player_stat in self.fbref.get_shoot_creation_stats(league_name):
                cur_player: PlayerStats = self.get_player(player_stat)
                if cur_player:
                    last3_sca_per_game, last3_gca_per_game, last5_sca_per_game, \
                    last5_gca_per_game = self.__compute_shoots_creation(player_stat, cur_player)

                    session.query(PlayerStats).filter(PlayerStats.id == cur_player.id).update({
                        'r5_sca': player_stat["sca"],
                        'r5_gca': player_stat["gca"],
                        'last3_sca_per_game': last3_sca_per_game,
                        'last3_gca_per_game': last3_gca_per_game,
                        'last5_sca_per_game': last5_sca_per_game,
                        'last5_gca_per_game': last5_gca_per_game
                    })
                else:  # if new player
                    session.add(PlayerStats(player_stat['name'], league_name, player_stat['team'],
                                            player_stat['position']))
                    session.commit()
                    cur_player = self.get_player(player_stat)
                    if cur_player:
                        session.query(PlayerStats).filter(PlayerStats.id == cur_player.id).update({
                            'r5_sca': player_stat["sca"],
                            'r5_gca': player_stat["gca"]
                        })
            return True
        except Exception as ex:
            # TODO logging
            print(ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return False
        finally:
            session.commit()
            session.close()

    def update_league(self, league_name: str, new_round: bool = False) -> bool:
        """
        Updates players stats for league
        """
        result: bool = True
        if league_name in self.fbref.shoots_leagues:
            result *= self.__update_shoots(league_name, new_round)
            result *= self.__update_shoots_files(league_name)

        if league_name in self.fbref.xg_leagues:
            result *= self.__update_xg(league_name)
            result *= self.__update_xg_files(league_name)

        if league_name in self.fbref.shoots_creation_leagues:
            result *= self.__update_shoots_creation(league_name)
            result *= self.__update_shoots_creation_files(league_name)
        return result

    def __update_files(self, league_name: str, stats_type: str, last_3_df, last_5_df) -> bool:
        try:
            cur_path = os.getcwd()
            # create paths
            league_path = os.path.join(cur_path, league_name)
            if not os.path.exists(league_path):
                os.mkdir(league_path)
            stat_path = os.path.join(league_path, stats_type)
            if not os.path.exists(stat_path):
                os.mkdir(stat_path)
            # save images
            dfi.export(last_3_df, os.path.join(stat_path, "last_3.png"))
            dfi.export(last_5_df, os.path.join(stat_path, "last_5.png"))
            return True
        except Exception as ex:
            # TODO logging
            print(ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return False

    def __update_shoots_files(self, league_name: str) -> bool:
        try:
            # get best players
            session: SQLSession = Session()
            best_players_last_3 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last3_shoots_per_game.desc(), PlayerStats.last3_on_target_per_shoot.desc()) \
                .limit(20).all()
            best_players_last_5 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last5_shoots_per_game.desc(), PlayerStats.last5_on_target_per_shoot.desc()) \
                .limit(20).all()
            # create pd pataframes
            last_3_info = [[player.last3_shoots_per_game, int(player.last3_on_target_per_shoot * 100),
                            player.name, player.team] for player in best_players_last_3]
            last_5_info = [[player.last5_shoots_per_game, int(player.last5_on_target_per_shoot * 100),
                            player.name, player.team] for player in best_players_last_5]

            last_3_df = pd.DataFrame(last_3_info, columns=['Уд/И', 'УдС/Уд(%)', 'Игрок', 'Команда'])
            last_3_df_styled = last_3_df.style.background_gradient()
            last_5_df = pd.DataFrame(last_5_info, columns=['Уд/И', 'УдС/Уд(%)', 'Игрок', 'Команда'])
            last_5_df_styled = last_5_df.style.background_gradient()

            result = self.__update_files(league_name, 'shoots', last_3_df_styled, last_5_df_styled)
            result *= asyncio.run(upload_files(os.getcwd(), league_name, 'shoots'))

            return result
        except Exception as ex:
            # TODO logging
            print(ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return False
        finally:
            session.close()

    def __update_xg_files(self, league_name: str) -> bool:
        try:
            # get best players
            session: SQLSession = Session()
            best_xg_last_3 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last3_xg_per_game.desc(), PlayerStats.last3_npxg_per_game.desc()) \
                .limit(20).all()
            best_xg_last_5 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last5_xg_per_game.desc(), PlayerStats.last5_npxg_per_game.desc()) \
                .limit(20).all()

            best_xg_xa_last_3 = session.query(PlayerStats, (PlayerStats.last3_xg_per_game +
                                                            PlayerStats.last3_xa_per_game).label('xg_xa')) \
                .filter(PlayerStats.league == league_name).order_by(xg_xa.desc()).limit(20).all()
            best_xg_xa_last_5 = session.query(PlayerStats, (PlayerStats.last5_xg_per_game +
                                                            PlayerStats.last5_xa_per_game).label('xg_xa')) \
                .filter(PlayerStats.league == league_name).order_by(xg_xa.desc()).limit(20).all()

            # create pd pataframes
            last_3_xg = [[player.last3_xg_per_game, player.last3_npxg_per_game, player.last3_xa_per_game,
                          player.name, player.team] for player in best_xg_last_3]
            last_5_xg = [[player.last5_xg_per_game, player.last5_npxg_per_game, player.last5_xa_per_game,
                          player.name, player.team] for player in best_xg_last_5]
            last_3_xg_xa = [[player.last3_xg_per_game + player.last3_xa_per_game, player.last3_npxg_per_game,
                             player.name, player.team] for player in best_xg_xa_last_3]
            last_5_xg_xa = [[player.last5_xg_per_game + player.last5_xa_per_game, player.last5_npxg_per_game,
                             player.name, player.team] for player in best_xg_xa_last_5]

            last_3_xg_df = pd.DataFrame(last_3_xg, columns=['xG', 'npxG', 'xA', 'Игрок', 'Команда'])
            last_3_xg_df_styled = last_3_xg_df.style.background_gradient()
            last_5_xg_df = pd.DataFrame(last_5_xg, columns=['xG', 'npxG', 'xA', 'Игрок', 'Команда'])
            last_5_xg_df_styled = last_5_xg_df.style.background_gradient()

            last_3_xg_xa_df = pd.DataFrame(last_3_xg_xa, columns=['xG+xA', 'npxG', 'Игрок', 'Команда'])
            last_3_xg_xa_df_styled = last_3_xg_xa_df.style.background_gradient()
            last_5_xg_xa_df = pd.DataFrame(last_5_xg_xa, columns=['xG+xA', 'npxG', 'Игрок', 'Команда'])
            last_5_xg_xa_df_styled = last_5_xg_xa_df.style.background_gradient()

            result = all([self.__update_files(league_name, 'xg', last_3_xg_df_styled, last_5_xg_df_styled),
                          self.__update_files(league_name, 'xg_xa', last_3_xg_xa_df_styled, last_5_xg_xa_df_styled)])

            result *= asyncio.run(upload_files(os.getcwd(), league_name, 'xg'))
            result *= asyncio.run(upload_files(os.getcwd(), league_name, 'xg_xa'))

            return result
        except Exception as ex:
            # TODO logging
            print(ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return False
        finally:
            session.close()

    def __update_shoots_creation_files(self, league_name: str) -> bool:
        try:
            # get best players
            session: SQLSession = Session()
            best_sca_last_3 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last3_sca_per_game.desc(), PlayerStats.last3_gca_per_game.desc()) \
                .limit(20).all()
            best_sca_last_5 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last5_sca_per_game.desc(), PlayerStats.last5_gca_per_game.desc()) \
                .limit(20).all()

            best_gca_last_3 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last3_gca_per_game.desc(), PlayerStats.last3_cca_per_game.desc()) \
                .limit(20).all()
            best_gca_last_5 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last5_gca_per_game.desc(), PlayerStats.last5_cca_per_game.desc()) \
                .limit(20).all()

            # create pd pataframes
            last_3_sca = [[player.last3_sca_per_game, player.last3_gca_per_game,
                           player.name, player.team] for player in best_sca_last_3]
            last_5_sca = [[player.last5_sca_per_game, player.last5_gca_per_game,
                           player.name, player.team] for player in best_sca_last_5]
            last_3_gca = [[player.last3_gca_per_game, player.last3_sca_per_game,
                           player.name, player.team] for player in best_gca_last_3]
            last_5_gca = [[player.last5_gca_per_game, player.last5_sca_per_game,
                           player.name, player.team] for player in best_gca_last_5]

            last_3_sca_df = pd.DataFrame(last_3_sca, columns=['sca', 'gca', 'Игрок', 'Команда'])
            last_3_sca_styled = last_3_sca_df.style.background_gradient()
            last_5_sca_df = pd.DataFrame(last_5_sca, columns=['sca', 'gca', 'Игрок', 'Команда'])
            last_5_sca_df_styled = last_5_sca_df.style.background_gradient()

            last_3_gca_df = pd.DataFrame(last_3_gca, columns=['gca', 'sca', 'Игрок', 'Команда'])
            last_3_gca_df_styled = last_3_gca_df.style.background_gradient()
            last_5_gca_df = pd.DataFrame(last_5_gca, columns=['gca', 'sca', 'Игрок', 'Команда'])
            last_5_gca_df_styled = last_5_gca_df.style.background_gradient()

            result = all([self.__update_files(league_name, 'sca', last_3_sca_styled, last_5_sca_df_styled),
                          self.__update_files(league_name, 'gca', last_3_gca_df_styled, last_5_gca_df_styled)])

            result *= asyncio.run(upload_files(os.getcwd(), league_name, 'sca'))
            result *= asyncio.run(upload_files(os.getcwd(), league_name, 'gca'))

            return result
        except Exception as ex:
            # TODO logging
            print(ex)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno)
            return False
        finally:
            session.close()

    def get_players_shoots_id(self, league_name: str, last_5: bool = False) -> str:
        if league_name not in self.fbref.shoots_leagues:
            return "Для данной лиги нет данных"

        # session: = ...
        # TODO


if __name__ == "__main__":
    psm = PlayerStatsManager()
    # print(psm.update_league("Russia", new_round=False))
    psm.update_league("Russia", False)
