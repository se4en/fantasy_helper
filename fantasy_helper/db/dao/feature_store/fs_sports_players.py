from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session as SQLSession

from fantasy_helper.db.models.feature_store.fs_sports_players import FSSportsPlayers
from fantasy_helper.db.database import Session
from fantasy_helper.utils.dataclasses import SportsPlayerDiff


class FSSportsPlayersDAO:
    def get_sports_players(self, league_name: str) -> List[SportsPlayerDiff]:
        db_session: SQLSession = Session()

        all_players = (
            db_session.query(FSSportsPlayers)
            .filter(FSSportsPlayers.league_name == league_name)
            .all()
        )

        result = [
            SportsPlayerDiff(
                name=player.name,
                league_name=player.league_name,
                team_name=player.team_name,
                role=player.role,
                price=player.price,
                percent_ownership=player.percent_ownership,
                percent_ownership_diff=player.percent_ownership_diff,
            )
            for player in all_players
        ]

        db_session.commit()
        db_session.close()

        return result

    def update_sports_players(self, league_name: str, players: List[SportsPlayerDiff]) -> None:
        db_session: SQLSession = Session()

        db_session.query(FSSportsPlayers).filter(
            FSSportsPlayers.league_name == league_name
        ).delete()

        for player in players:
            db_session.add(FSSportsPlayers(**player.__dict__))

        db_session.commit()
        db_session.close()

    def get_min_price(self, league_name: str) -> float:
        db_session: SQLSession = Session()

        min_price = (
            db_session.query(FSSportsPlayers.price)
            .filter(FSSportsPlayers.league_name == league_name)
            .order_by(FSSportsPlayers.price)
            .first()
        )

        db_session.commit()
        db_session.close()

        return min_price[0]

    def get_max_price(self, league_name: str) -> float:
        db_session: SQLSession = Session()

        max_price = (
            db_session.query(FSSportsPlayers.price)
            .filter(FSSportsPlayers.league_name == league_name)
            .order_by(FSSportsPlayers.price.desc())
            .first()
        )

        db_session.commit()
        db_session.close()

        return max_price[0]
