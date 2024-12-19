
from typing import List, Optional
from fantasy_helper.db.models.coeff import Coeff
from fantasy_helper.db.models.player import Player
from sqlalchemy.orm import Session as SQLSession

from fantasy_helper.db.models.sports_player import SportsPlayer
from fantasy_helper.utils.common import load_config
from fantasy_helper.db.database import Session


class NameMatcher:
    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")
        
    def get_sports_teams_names(self, league_name: str) -> Optional[List[str]]:
        db_session: SQLSession = Session()

        query = (
            db_session.query(SportsPlayer.team_name).filter(
                SportsPlayer.league_name == league_name
            )
            .distinct()
            .order_by(SportsPlayer.team_name)
        )
        team_names = query.all()

        db_session.close()

        return team_names

    def get_fbref_teams_names(self, league_name: str) -> Optional[List[str]]:
        db_session: SQLSession = Session()

        query = (
            db_session.query(Player.team_name).filter(
                Player.league_name == league_name
            )
            .distinct()
            .order_by(Player.team_name)
        )
        team_names = query.all()

        db_session.close()

        return [elem[0] for elem in team_names]

    def get_xbet_teams_names(self, league_name: str) -> Optional[List[str]]:
        db_session: SQLSession = Session()

        query = (
            db_session.query(Coeff.home_team).filter(
                Coeff.league_name == league_name
            )
            .distinct()
            .order_by(Coeff.home_team)
        )
        team_names = query.all()

        db_session.close()

        return [elem[0] for elem in team_names]


if __name__ == "__main__":
    matcher = NameMatcher()
    print(matcher.get_sports_teams_names("Russia"))
    print(matcher.get_fbref_teams_names("Russia"))
    print(matcher.get_xbet_teams_names("Russia"))
