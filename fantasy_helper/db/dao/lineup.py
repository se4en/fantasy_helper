from typing import List
from datetime import datetime, timezone
from dataclasses import asdict

from sqlalchemy import func, and_
from sqlalchemy.orm import Session as SQLSession
from hydra import compose, initialize
from hydra.core.global_hydra import GlobalHydra

from fantasy_helper.db.models.lineup import Lineup
from fantasy_helper.db.database import Session
from fantasy_helper.parsers.mole import MoleParser
from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import LeagueInfo, TeamLineup
from fantasy_helper.db.dao.feature_store.fs_lineups import FSLineupsDAO


utc = timezone.utc


class LineupDAO:
    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")

        self.__leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._league_2_year = {league.name: league.year for league in self.__leagues}
        self.__mole_parser = MoleParser(leagues=self.__leagues)

    def get_lineups(self, league_name: str) -> List[TeamLineup]:
        year = self._league_2_year.get(league_name, "2024")

        db_session: SQLSession = Session()

        last_row = db_session.query(Lineup).order_by(Lineup.timestamp.desc()).first()
        if last_row is not None:
            last_update_id = last_row.update_id
        else:
            last_update_id = -1

        cur_league_rows = (
            db_session.query(Lineup)
            .filter(and_(
                Lineup.league_name == league_name, 
                Lineup.year == year, 
                Lineup.update_id == last_update_id
            ))
            .subquery()
        )

        grouped_by_team = db_session.query(
            cur_league_rows,
            func.rank()
            .over(
                order_by=cur_league_rows.c.timestamp.desc(),
                partition_by=cur_league_rows.c.team_name,
            )
            .label("rnk"),
        ).subquery()

        latest_lineups = (
            db_session.query(grouped_by_team).filter(grouped_by_team.c.rnk == 1).all()
        )

        result = [
            TeamLineup(
                team_name=lineup.team_name,
                league_name=lineup.league_name,
                lineup=lineup.lineup,
            )
            for lineup in latest_lineups
        ]

        db_session.commit()
        db_session.close()

        return result

    def update_lineups_all_leagues(self) -> None:
        new_lineups: List[TeamLineup] = self.__mole_parser.get_lineups()
        db_session: SQLSession = Session()

        last_row = db_session.query(Lineup).order_by(Lineup.timestamp.desc()).first()
        if last_row is not None:
            new_update_id = last_row.update_id + 1
        else:
            new_update_id = 0

        for lineup in new_lineups:
            year = self._league_2_year.get(lineup.league_name, "2024")
            db_session.add(
                Lineup(
                    **asdict(lineup),
                    update_id=new_update_id,
                    timestamp=datetime.now().replace(tzinfo=utc),
                    year=year
                )
            )

        db_session.commit()
        db_session.close()

    def update_feature_store(self) -> None:
        feature_store = FSLineupsDAO()

        for league in self.__leagues:
            league_lineups = self.get_lineups(league.name)
            feature_store.update_lineups(league.name, league_lineups)
