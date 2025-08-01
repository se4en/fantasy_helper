from dataclasses import asdict
from datetime import datetime, timezone
from typing import List
import os.path as path

from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import and_, func, or_

from fantasy_helper.db.database import Session
from fantasy_helper.db.models.fbref_schedule import FbrefSchedule
from fantasy_helper.db.dao.players_match import PlayersMatchDao
from fantasy_helper.parsers.fbref import FbrefParser
from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import LeagueInfo, LeagueScheduleInfo

utc = timezone.utc


class FbrefScheduleDao:
    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")

        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._league_2_year = {league.name: league.year for league in self._leagues}
        self._fbref_parser = FbrefParser(leagues=self._leagues)
        self._players_match_dao = PlayersMatchDao()

    def get_leagues(self) -> List[str]:
        return [league.name for league in self._leagues]
    
    def remove_unparsed_matches(self, league_name: str) -> None:
        year = self._league_2_year.get(league_name, "2024")

        db_session: SQLSession = Session()

        db_session.query(FbrefSchedule).filter(
            and_(
                FbrefSchedule.league_name == league_name,
                FbrefSchedule.year == year,
                FbrefSchedule.match_parsed == False
            )
        ).delete()

        db_session.commit()
        db_session.close()

    def add_new_matches(self, matches: List[LeagueScheduleInfo]) -> None:
        db_session: SQLSession = Session()

        for match in matches:
            year = self._league_2_year.get(match.league_name, "2024")
            db_session.add(FbrefSchedule(
                **asdict(match),
                timestamp=datetime.now().replace(tzinfo=utc),
                year=year
            ))

        db_session.commit()
        db_session.close()

    def get_parsed_matches(self, league_name: str) -> List[LeagueScheduleInfo]:
        year = self._league_2_year.get(league_name, "2024")

        db_session: SQLSession = Session()

        parsed_matches = (
            db_session.query(FbrefSchedule)
            .filter(and_(
                FbrefSchedule.league_name == league_name,
                FbrefSchedule.year == year,
                FbrefSchedule.match_parsed == True
            ))
            .all()
        )

        result = [
            LeagueScheduleInfo(
                league_name=schedule_row.league_name,
                home_team=schedule_row.home_team,
                away_team=schedule_row.away_team,
                gameweek=schedule_row.gameweek,
                date=schedule_row.date,
                home_goals=schedule_row.home_goals,
                away_goals=schedule_row.away_goals,
                match_url=schedule_row.match_url,
                match_parsed=schedule_row.match_parsed
            ) 
            for schedule_row in parsed_matches
        ]

        db_session.commit()
        db_session.close()

        return result

    def update_schedules_all_leagues(self) -> None:
        for league_name, _ in self._fbref_parser.get_schedule_leagues().items():
            year = self._league_2_year.get(league_name, "2024")
            cup = False
            if league_name == "ChampionsLeague" or league_name == "EuropaLeague" or league_name == "ClubWorldCup":
                cup = True
            schedule_rows: List[LeagueScheduleInfo] = self._fbref_parser.get_league_schedule(
                league_name=league_name, cup=cup, league_year=year
            )

            parsed_matches = set(map(hash, self.get_parsed_matches(league_name=league_name)))

            matches_2_parse, matches_2_add = [], []
            for schedule_row in schedule_rows:
                if hash(schedule_row) not in parsed_matches:
                    if schedule_row.match_url is not None:
                        matches_2_parse.append(schedule_row)
                    else:
                        matches_2_add.append(schedule_row)

            matches_after_parse = self._players_match_dao.parse_matches(
                league_name, matches_2_parse
            )

            self.remove_unparsed_matches(league_name=league_name)
            self.add_new_matches(matches_after_parse + matches_2_add)
