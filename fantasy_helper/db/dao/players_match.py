from dataclasses import asdict
from datetime import datetime, timezone
from typing import List
from copy import deepcopy
import os.path as path

from fantasy_helper.utils.dataclasses import LeagueInfo, LeagueScheduleInfo, PlayerMatchStats, PlayerStats
from sqlalchemy.orm import Session as SQLSession
from sqlalchemy import and_, func, or_

from fantasy_helper.db.database import Session
from fantasy_helper.db.models.players_match import PlayersMatch
from fantasy_helper.parsers.fbref import FbrefParser
from fantasy_helper.utils.common import instantiate_leagues, load_config


utc = timezone.utc


class PlayersMatchDao:
    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")

        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._fbref_parser = FbrefParser(leagues=self._leagues)

    def get_leagues(self) -> List[str]:
        return [league.name for league in self._leagues]
    
    def _add_match_info_to_player(
        self, players: List[PlayerMatchStats], match: LeagueScheduleInfo
    ) -> List[PlayerMatchStats]:
        result = []

        for player in players:
            new_player = deepcopy(player)
            new_player.home_team = match.home_team
            new_player.away_team = match.away_team
            new_player.gameweek = match.gameweek
            new_player.date = match.date
            new_player.match_url = match.match_url
            result.append(new_player)

        return result

    def parse_matches(
        self, league_name: str, matches: List[LeagueScheduleInfo]
    ) -> List[LeagueScheduleInfo]:
        result = []

        for match in matches:
            if match.match_url is not None:
                match_players = self._fbref_parser.parse_match_stats(match.match_url, league_name)

            else:
                match_players = None

            new_match = deepcopy(match)
            if match_players:
                new_match.match_parsed = True
                match_players = self._add_match_info_to_player(match_players, new_match)
                self.add_match_players(match_players)
            else:
                new_match.match_parsed = False

            result.append(new_match)

        return result

    def add_match_players(self, players_matches: List[PlayerMatchStats]) -> None:
        db_session: SQLSession = Session()

        for players_match in players_matches:
            db_session.add(
                PlayersMatch(
                    **asdict(players_match), timestamp=datetime.now().replace(tzinfo=utc)
                )
            )

        db_session.commit()
        db_session.close()
