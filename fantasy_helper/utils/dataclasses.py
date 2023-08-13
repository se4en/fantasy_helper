from dataclasses import dataclass
from datetime import datetime
import typing as t


@dataclass
class MatchInfo:
    url: str
    league_name: str
    home_team: str
    away_team: str
    start_datetime: t.Optional[datetime] = None
    total_1_over_1_5: t.Optional[float] = None
    total_1_under_0_5: t.Optional[float] = None
    total_2_over_1_5: t.Optional[float] = None
    total_2_under_0_5: t.Optional[float] = None


@dataclass
class LeagueInfo:
    name: str
    ru_name: str
    emoji: str
    squad_id: t.Optional[int] = None
    xber_url: t.Optional[str] = None
    fbref_shoots_url: t.Optional[str] = None
    fbref_xg_url: t.Optional[str] = None
    fbref_shoots_creation_url: t.Optional[str] = None
    sportsmole_name: t.Optional[str] = None


@dataclass
class TeamLineup:
    team_name: str
    league_name: str
    lineup: str
