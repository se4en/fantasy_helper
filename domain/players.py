import os
import sys
from datetime import datetime, timedelta
from typing import List
from aiogram.utils.emoji import emojize
from aiogram.utils.markdown import bold
from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from db.database import Session
from db.parse.sports import Sports
from db.parse.xbet import XBet
from domain.manager import Manager
from db.models.player import Player


class PlayerManager(Manager):

    def __init__(self):
        super().__init__()
        self.sports = Sports()

    def get_player(self, player_info: dict) -> Player:
        session: SQLSession = Session()
        result = session.query(Player).filter(and_(Player.name == player_info['name'],
                                                   Player.league == player_info['league'],
                                                   Player.team == player_info['team'],
                                                   Player.amplua == player_info['amplua'])).first()
        session.close()
        return result


    def update_league(self, league_name: str, new_round: bool = False) -> bool:
        """
        Updates players popularity for league
        """
        session: SQLSession = Session()
        try:
            # TODO delete this
            # league_info = session.query(League_info).filter(League_info.league == league_name).first()
            # if not league_info:
            #     return False

            for player in self.sports.get_league_players(league_name):
                cur_player = self.get_player(player)
                if cur_player:
                    if new_round:
                        session.query(Player).filter(Player.id == cur_player.id).update(
                            {'old_popularity': player['popularity'], 'dif_popularity': 0})
                    else:
                        session.query(Player).filter(Player.id == cur_player.id).update(
                            {'dif_popularity': player['popularity'] - Player.old_popularity})
                else:  # if new player
                    session.add(Player(player['name'], player['league'], player['team'],
                                       player['amplua'], player['popularity'], 0))
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

    def get_players(self, league_name: str) -> str:
        xbet = XBet()
        if league_name not in xbet.leagues:
            return "Ошибка в названии лиги"

        session: SQLSession = Session()
        best_players = session.query(Player).filter(Player.league == league_name) \
            .order_by(Player.dif_popularity.desc(), Player.old_popularity.desc()).limit(10).all()
        worst_players = session.query(Player).filter(Player.league == league_name) \
            .order_by(Player.dif_popularity, Player.old_popularity.desc()).limit(10).all()
        session.close()

        result = ["\U0001F4C8 Популярные игроки:\n"]
        result += self.__transform_players(best_players)
        result += ["\n\U0001F4C9 Непопулярные игроки:\n"]
        result += self.__transform_players(worst_players)
        return '\n'.join(result)

    def __transform_players(self, players_list: List[Player]) -> List[str]:
        result = []
        for i, player in enumerate(players_list):
            if player.dif_popularity < 0:
                result += [emojize(f"{self.emojize_number(i+1)} {player.dif_popularity}" +
                           bold(f" {player.name}"))]
            else:
                result += [emojize(f"{self.emojize_number(i+1)} +{player.dif_popularity}" +
                           bold(f" {player.name}"))]
        return result


if __name__ == "__main__":
    pm = PlayerManager()
    # print(pm.get_players("Russia"))
    print(pm.update_league("Russia"))
