from dataclasses import asdict
from typing import List
from datetime import datetime, timezone

from sqlalchemy.orm import Session as SQLSession

from fantasy_helper.utils.common import instantiate_leagues, load_config
from fantasy_helper.utils.dataclasses import LeagueInfo, PlayerName, TeamName, PlayersLeagueStats
from fantasy_helper.db.database import Session
from fantasy_helper.db.models.ml.player_name import PlayerName as DBPlayerName
from fantasy_helper.db.models.ml.team_name import TeamName as DBTeamName
from fantasy_helper.ml.naming.name_matcher import NameMatcher


utc = timezone.utc


class NamingDAO:
    def __init__(self):
        cfg = load_config(config_path="../../conf", config_name="config")
        self._leagues: List[LeagueInfo] = instantiate_leagues(cfg)
        self._name_matcher = NameMatcher()

    def update_league_naming(self, league_name: str) -> None:
        db_session: SQLSession = Session()

        # clean previous names
        db_session.query(DBTeamName).filter(DBTeamName.league_name == league_name).delete()
        db_session.query(DBPlayerName).filter(DBPlayerName.league_name == league_name).delete()

        teams_names = self._name_matcher.match_teams(league_name)
        for team_name in teams_names:
            # update team names
            db_session.add(DBTeamName(
                timestamp=datetime.now().replace(tzinfo=utc), 
                **asdict(team_name)
            ))

            # update players names
            players_names = self._name_matcher.match_players(league_name, team_name)
            for player_name in players_names:
                db_session.add(DBPlayerName(
                    timestamp=datetime.now().replace(tzinfo=utc), 
                    **asdict(player_name)
                ))

        db_session.commit()
        db_session.close()

    def update_naming_all_leagues(self) -> None:
        for league in self._leagues:
            self.update_league_naming(league.name)

    def get_teams(self, league_name: str) -> List[TeamName]:
        db_session: SQLSession = Session()

        teams = (
            db_session.query(DBTeamName)
            .filter(DBTeamName.league_name == league_name)
            .all()
        )

        db_session.commit()
        db_session.close()

        result = [
            TeamName(
                league_name=team.league_name,
                sports_name=team.sports_name,
                fbref_name=team.fbref_name,
                xbet_name=team.xbet_name,
                name=team.name
            ) 
            for team in teams
        ]
        return result

    def get_players(self, league_name: str) -> List[PlayerName]:
        db_session: SQLSession = Session()

        players = (
            db_session.query(DBPlayerName)
            .filter(DBPlayerName.league_name == league_name)
            .all()
        )

        db_session.commit()
        db_session.close()

        result = [
            PlayerName(
                league_name=player.league_name,
                team_name=player.team_name,
                sports_name=player.sports_name,
                fbref_name=player.fbref_name,
                name=player.name
            ) 
            for player in players
        ]
        return result
