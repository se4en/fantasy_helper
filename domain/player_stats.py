import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import List
import pandas as pd
import numpy as np
import dataframe_image as dfi
from sqlalchemy import and_, desc
from sqlalchemy.orm import Session as SQLSession
from sqlalchemy.sql import label

from db.database import Session
from db.parse.fbref import FbrefParser
from domain.manager import Manager
from db.models.player_stats import PlayerStats
from db.models.media_ids import MediaIds
from db.utils.uploding_files import upload_files, get_git_root
from db.models.leagues_info import League_info
from loader import STATS_DATA_PATH


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

    def __update_player(self, cur_player: PlayerStats) -> bool:
        """
        Update player stats for next round
        """
        session: SQLSession = Session()
        try:
            session.query(PlayerStats).filter(PlayerStats.id == cur_player.id).update({
                # round 0
                'r0_minutes': cur_player.r1_minutes,
                'r0_shoots': cur_player.r1_shoots,
                'r0_shoots_on_target': cur_player.r1_shoots_on_target,
                'r0_xg': cur_player.r1_xg,
                'r0_npxg': cur_player.r1_npxg,
                'r0_xa': cur_player.r1_xa,
                'r0_sca': cur_player.r1_sca,
                'r0_gca': cur_player.r1_gca,
                # round 1
                'r1_minutes': cur_player.r2_minutes,
                'r1_shoots': cur_player.r2_shoots,
                'r1_shoots_on_target': cur_player.r2_shoots_on_target,
                'r1_xg': cur_player.r2_xg,
                'r1_npxg': cur_player.r2_npxg,
                'r1_xa': cur_player.r2_xa,
                'r1_sca': cur_player.r2_sca,
                'r1_gca': cur_player.r2_gca,
                # round 2
                'r2_minutes': cur_player.r3_minutes,
                'r2_shoots': cur_player.r3_shoots,
                'r2_shoots_on_target': cur_player.r3_shoots_on_target,
                'r2_xg': cur_player.r3_xg,
                'r2_npxg': cur_player.r3_npxg,
                'r2_xa': cur_player.r3_xa,
                'r2_sca': cur_player.r3_sca,
                'r2_gca': cur_player.r3_gca,
                # round 3
                'r3_minutes': cur_player.r4_minutes,
                'r3_shoots': cur_player.r4_shoots,
                'r3_shoots_on_target': cur_player.r4_shoots_on_target,
                'r3_xg': cur_player.r4_xg,
                'r3_npxg': cur_player.r4_npxg,
                'r3_xa': cur_player.r4_xa,
                'r3_sca': cur_player.r4_sca,
                'r3_gca': cur_player.r4_gca,
                # round 4
                'r4_minutes': cur_player.r5_minutes,
                'r4_shoots': cur_player.r5_shoots,
                'r4_shoots_on_target': cur_player.r5_shoots_on_target,
                'r4_xg': cur_player.r5_xg,
                'r4_npxg': cur_player.r5_npxg,
                'r4_xa': cur_player.r5_xa,
                'r4_sca': cur_player.r5_sca,
                'r4_gca': cur_player.r5_gca,
            })
            session.commit()
            return True
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            session.commit()
            session.close()

    def __compute_shoots(self, player_info: dict, player_stat: PlayerStats):
        last3_minutes = player_info["minutes"] - player_stat.r2_minutes
        last3_shoots = player_info["shots_total"] - player_stat.r2_shoots
        if last3_minutes < self.LAST3_MIN:
            last3_minutes = 0
            last3_shoots = 0

        if last3_minutes > 0:
            last3_shoots_per_game = last3_shoots / last3_minutes
        else:
            last3_shoots_per_game = 0
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

        if last5_minutes > 0:
            last5_shoots_per_game = last5_shoots / last5_minutes
        else:
            last5_shoots_per_game = 0
        if last5_shoots == 0:
            last5_on_target_per_shoot = 0
        else:
            last5_on_target_per_shoot = (player_info["shots_on_target"] -
                                         player_stat.r0_shoots_on_target) / last5_shoots

        return (last3_shoots_per_game, last3_on_target_per_shoot,
                last5_shoots_per_game, last5_on_target_per_shoot)

    def __update_shoots(self, league_name: str, new_round: bool = False) -> bool:
        logging.info(f"Start update shoots for league={league_name}")
        session: SQLSession = Session()
        try:
            for player_stat in self.fbref.get_shooting_stats(league_name):
                cur_player: PlayerStats = self.get_player(player_stat)
                if cur_player:
                    if new_round:
                        if self.__update_player(cur_player):
                            # session.refresh(cur_player)
                            cur_player: PlayerStats = self.get_player(player_stat)
                        else:
                            logging.warning(f"Something wrong when updating palyer {cur_player}")
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
                    session.commit()
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
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            session.commit()
            session.close()

    def __compute_xg(self, player_info: dict, player_stat: PlayerStats):
        last3_minutes = player_stat.r5_minutes - player_stat.r2_minutes
        if last3_minutes < self.LAST3_MIN:
            last3_minutes = 0
        if last3_minutes > 0:
            last3_xg_per_game = (player_info["xg"] - player_stat.r2_xg) / last3_minutes
            last3_npxg_per_game = (player_info["npxg"] - player_stat.r2_npxg) / last3_minutes
            last3_xa_per_game = (player_info["xa"] - player_stat.r2_xa) / last3_minutes
        else:
            last3_xg_per_game, last3_npxg_per_game, last3_xa_per_game = 0, 0, 0

        last5_minutes = player_stat.r5_minutes - player_stat.r0_minutes
        if last5_minutes < self.LAST5_MIN:
            last5_minutes = 0
        if last5_minutes > 0:
            last5_xg_per_game = (player_info["xg"] - player_stat.r0_xg) / last5_minutes
            last5_npxg_per_game = (player_info["npxg"] - player_stat.r0_npxg) / last5_minutes
            last5_xa_per_game = (player_info["xa"] - player_stat.r0_xa) / last5_minutes
        else:
            last5_xg_per_game, last5_npxg_per_game, last5_xa_per_game = 0, 0, 0

        return (last3_xg_per_game, last3_npxg_per_game, last3_xa_per_game,
                last5_xg_per_game, last5_npxg_per_game, last5_xa_per_game)

    def __update_xg(self, league_name: str) -> bool:
        logging.info(f"Start update xg for league={league_name}")
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
                    session.commit()
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
                        session.commit()
            return True
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            session.commit()
            session.close()

    def __compute_shoots_creation(self, player_info: dict, player_stat: PlayerStats):
        last3_minutes = player_stat.r5_minutes - player_stat.r2_minutes
        if last3_minutes < self.LAST3_MIN:
            last3_minutes = 0
        if last3_minutes > 0:
            last3_sca_per_game = (player_info["sca"] - player_stat.r2_sca) / last3_minutes
            last3_gca_per_game = (player_info["gca"] - player_stat.r2_gca) / last3_minutes
        else:
            last3_sca_per_game, last3_gca_per_game = 0, 0

        last5_minutes = player_stat.r5_minutes - player_stat.r0_minutes
        if last5_minutes < self.LAST5_MIN:
            last5_minutes = 0
        if last5_minutes > 0:
            last5_sca_per_game = (player_info["sca"] - player_stat.r0_sca) / last5_minutes
            last5_gca_per_game = (player_info["gca"] - player_stat.r0_gca) / last5_minutes
        else:
            last5_sca_per_game, last5_gca_per_game = 0, 0

        return last3_sca_per_game, last3_gca_per_game, last5_sca_per_game, last5_gca_per_game

    def __update_shoots_creation(self, league_name: str) -> bool:
        logging.info(f"Start update shoot creation for league={league_name}")
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
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            session.commit()
            session.close()

    async def update_league(self, league_name: str, new_round: bool = False) -> bool:
        """
        Updates players stats for league
        """
        logging.info(f"Start update all stats for league={league_name}, new_round={new_round}")
        result: bool = True
        if league_name in self.fbref.shoots_leagues:
            result *= self.__update_shoots(league_name, new_round)
            result *= await self.__update_shoots_files(league_name)

        if league_name in self.fbref.xg_leagues:
            result *= self.__update_xg(league_name)
            result *= await self.__update_xg_files(league_name)

        if league_name in self.fbref.shoots_creation_leagues:
            result *= self.__update_shoots_creation(league_name)
            result *= await self.__update_shoots_creation_files(league_name)
        return result

    def __update_files(self, league_name: str, stats_type: str, last_3_df, last_5_df) -> bool:
        try:
            base_path = STATS_DATA_PATH
            # create paths
            if not os.path.exists(base_path):
                os.mkdir(base_path)
            league_path = os.path.join(STATS_DATA_PATH, league_name)
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
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False

    async def __update_shoots_files(self, league_name: str) -> bool:
        try:
            logging.info(f"Start update shoots files for league={league_name}")
            # get best players
            session: SQLSession = Session()
            best_players_last_3 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last3_shoots_per_game.desc(), PlayerStats.last3_on_target_per_shoot.desc()) \
                .limit(20).all()
            best_players_last_5 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last5_shoots_per_game.desc(), PlayerStats.last5_on_target_per_shoot.desc()) \
                .limit(20).all()
            # create pd pataframes
            last_3_info = [[round(player.last3_shoots_per_game, 2), int(player.last3_on_target_per_shoot * 100),
                            player.name, player.team] for player in best_players_last_3]
            last_5_info = [[round(player.last5_shoots_per_game, 2), int(player.last5_on_target_per_shoot * 100),
                            player.name, player.team] for player in best_players_last_5]

            last_3_df = pd.DataFrame(last_3_info, columns=['Уд/И', 'УдС/Уд(%)', 'Игрок', 'Команда'])
            last_3_df_styled = last_3_df.style.background_gradient()
            last_5_df = pd.DataFrame(last_5_info, columns=['Уд/И', 'УдС/Уд(%)', 'Игрок', 'Команда'])
            last_5_df_styled = last_5_df.style.background_gradient()

            result = self.__update_files(league_name, 'shoots', last_3_df_styled, last_5_df_styled)
            result *= await upload_files(league_name, 'shoots')

            return result
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            session.close()

    async def __update_xg_files(self, league_name: str) -> bool:
        try:
            logging.info(f"Start update xg files for league={league_name}")
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
                .filter(PlayerStats.league == league_name).order_by(desc('xg_xa')).limit(20).all()
            best_xg_xa_last_5 = session.query(PlayerStats, (PlayerStats.last5_xg_per_game +
                                                            PlayerStats.last5_xa_per_game).label('xg_xa')) \
                .filter(PlayerStats.league == league_name).order_by(desc('xg_xa')).limit(20).all()

            # create pd pataframes
            last_3_xg = [[round(player.last3_xg_per_game, 2), round(player.last3_npxg_per_game, 2),
                          round(player.last3_xa_per_game, 2), player.name, player.team]
                         for player in best_xg_last_3]
            last_5_xg = [[round(player.last5_xg_per_game, 2), round(player.last5_npxg_per_game, 2),
                          round(player.last5_xa_per_game, 2), player.name, player.team]
                         for player in best_xg_last_5]

            last_3_xg_xa = [[round(player[1], 2),
                             round(player[0].last3_npxg_per_game, 2), player[0].name, player[0].team]
                            for player in best_xg_xa_last_3]
            last_5_xg_xa = [[round(player[1], 2),
                             round(player[0].last5_npxg_per_game, 2), player[0].name, player[0].team]
                            for player in best_xg_xa_last_5]

            last_3_xg_df = pd.DataFrame(last_3_xg, columns=['xG/И', 'npxG/И', 'xA/И', 'Игрок', 'Команда'])
            last_3_xg_df_styled = last_3_xg_df.style.background_gradient()
            last_5_xg_df = pd.DataFrame(last_5_xg, columns=['xG/И', 'npxG/И', 'xA/И', 'Игрок', 'Команда'])
            last_5_xg_df_styled = last_5_xg_df.style.background_gradient()

            last_3_xg_xa_df = pd.DataFrame(last_3_xg_xa, columns=['xG+xA/И', 'npxG/И', 'Игрок', 'Команда'])
            last_3_xg_xa_df_styled = last_3_xg_xa_df.style.background_gradient()
            last_5_xg_xa_df = pd.DataFrame(last_5_xg_xa, columns=['xG+xA/И', 'npxG/И', 'Игрок', 'Команда'])
            last_5_xg_xa_df_styled = last_5_xg_xa_df.style.background_gradient()

            result = all([self.__update_files(league_name, 'xg', last_3_xg_df_styled, last_5_xg_df_styled),
                          self.__update_files(league_name, 'xg_xa', last_3_xg_xa_df_styled, last_5_xg_xa_df_styled)])

            result *= await upload_files(league_name, 'xg')
            result *= await upload_files(league_name, 'xg_xa')

            return result
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            session.close()

    async def __update_shoots_creation_files(self, league_name: str) -> bool:
        try:
            logging.info(f"Start update shoot creation files for league={league_name}")
            # get best players
            session: SQLSession = Session()
            best_sca_last_3 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last3_sca_per_game.desc(), PlayerStats.last3_gca_per_game.desc()) \
                .limit(20).all()
            best_sca_last_5 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last5_sca_per_game.desc(), PlayerStats.last5_gca_per_game.desc()) \
                .limit(20).all()

            best_gca_last_3 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last3_gca_per_game.desc(), PlayerStats.last3_sca_per_game.desc()) \
                .limit(20).all()
            best_gca_last_5 = session.query(PlayerStats).filter(PlayerStats.league == league_name) \
                .order_by(PlayerStats.last5_gca_per_game.desc(), PlayerStats.last5_sca_per_game.desc()) \
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

            last_3_sca_df = pd.DataFrame(last_3_sca, columns=['sca/И', 'gca/И', 'Игрок', 'Команда'])
            last_3_sca_styled = last_3_sca_df.style.background_gradient()
            last_5_sca_df = pd.DataFrame(last_5_sca, columns=['sca/И', 'gca/И', 'Игрок', 'Команда'])
            last_5_sca_df_styled = last_5_sca_df.style.background_gradient()

            last_3_gca_df = pd.DataFrame(last_3_gca, columns=['gca/И', 'sca/И', 'Игрок', 'Команда'])
            last_3_gca_df_styled = last_3_gca_df.style.background_gradient()
            last_5_gca_df = pd.DataFrame(last_5_gca, columns=['gca/И', 'sca/И', 'Игрок', 'Команда'])
            last_5_gca_df_styled = last_5_gca_df.style.background_gradient()

            result = all([self.__update_files(league_name, 'sca', last_3_sca_styled, last_5_sca_df_styled),
                          self.__update_files(league_name, 'gca', last_3_gca_df_styled, last_5_gca_df_styled)])

            result *= await upload_files(league_name, 'sca')
            result *= await upload_files(league_name, 'gca')

            return result
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return False
        finally:
            session.close()

    def get_players_shoots_id(self, league_name: str, last_5: bool = False) -> str:
        if league_name not in self.fbref.shoots_leagues:
            return "Для данной лиги нет данных"

        try:
            session: SQLSession = Session()
            image = session.query(MediaIds).filter(and_(MediaIds.league == league_name,
                                                        MediaIds.stat_type == 'shoots',
                                                        MediaIds.last_5 == last_5)).first()
            if image is not None:
                return image.file_id
            else:
                return ""
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return ""
        finally:
            session.close()

    def get_xg_id(self, league_name: str, last_5: bool = False) -> str:
        if league_name not in self.fbref.xg_leagues:
            return "Для данной лиги нет данных"

        try:
            session: SQLSession = Session()
            image = session.query(MediaIds).filter(and_(MediaIds.league == league_name,
                                                        MediaIds.stat_type == 'xg',
                                                        MediaIds.last_5 == last_5)).first()
            if image is not None:
                return image.file_id
            else:
                return ""
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return ""
        finally:
            session.close()

    def get_xg_xa_id(self, league_name: str, last_5: bool = False) -> str:
        if league_name not in self.fbref.xg_leagues:
            return "Для данной лиги нет данных"

        try:
            session: SQLSession = Session()
            image = session.query(MediaIds).filter(and_(MediaIds.league == league_name,
                                                        MediaIds.stat_type == 'xg_xa',
                                                        MediaIds.last_5 == last_5)).first()
            if image is not None:
                return image.file_id
            else:
                return ""
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return ""
        finally:
            session.close()

    def get_sca_id(self, league_name: str, last_5: bool = False) -> str:
        if league_name not in self.fbref.shoots_creation_leagues:
            return "Для данной лиги нет данных"

        try:
            session: SQLSession = Session()
            image = session.query(MediaIds).filter(and_(MediaIds.league == league_name,
                                                        MediaIds.stat_type == 'sca',
                                                        MediaIds.last_5 == last_5)).first()
            if image is not None:
                return image.file_id
            else:
                return ""
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return ""
        finally:
            session.close()

    def get_gca_id(self, league_name: str, last_5: bool = False) -> str:
        if league_name not in self.fbref.shoots_creation_leagues:
            return "Для данной лиги нет данных"

        try:
            session: SQLSession = Session()
            image = session.query(MediaIds).filter(and_(MediaIds.league == league_name,
                                                        MediaIds.stat_type == 'gca',
                                                        MediaIds.last_5 == last_5)).first()
            if image is not None:
                return image.file_id
            else:
                return ""
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            return ""
        finally:
            session.close()


if __name__ == "__main__":
    psm = PlayerStatsManager()
    asyncio.run(psm.update_league("Italy", new_round=False))
    # print(psm.update_league("Russia", new_round=False))
    # await psm.update_league("Russia", False)
    # session: SQLSession = Session()
    # session.query(PlayerStats).update({
    #     # round 0
    #     PlayerStats.r3_minutes: PlayerStats.r2_minutes,
    #     PlayerStats.r3_shoots: PlayerStats.r2_shoots,
    #     PlayerStats.r3_shoots_on_target: PlayerStats.r2_shoots_on_target,
    #     PlayerStats.r3_xg: PlayerStats.r2_xg,
    #     PlayerStats.r3_npxg: PlayerStats.r2_npxg,
    #     PlayerStats.r3_xa: PlayerStats.r2_xa,
    #     PlayerStats.r3_sca: PlayerStats.r2_sca,
    #     PlayerStats.r3_gca: PlayerStats.r2_gca,

    #     PlayerStats.r2_minutes: 0,
    #     PlayerStats.r2_shoots: 0,
    #     PlayerStats.r2_shoots_on_target: 0,
    #     PlayerStats.r2_xg: 0,
    #     PlayerStats.r2_npxg: 0,
    #     PlayerStats.r2_xa: 0,
    #     PlayerStats.r2_sca: 0,
    #     PlayerStats.r2_gca: 0,
    # })
    # session.commit()
    # session.close()
