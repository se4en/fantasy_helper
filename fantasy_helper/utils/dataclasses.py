from dataclasses import dataclass
from datetime import datetime, date
from typing import List, Optional, Dict

import pandas as pd


@dataclass
class MatchInfo:
    url: str
    league_name: str
    home_team: str
    away_team: str
    start_datetime: Optional[datetime] = None
    tour_number: Optional[int] = None

    result_1: Optional[float] = None
    result_x: Optional[float] = None
    result_2: Optional[float] = None

    both_score_yes: Optional[float] = None
    both_score_no: Optional[float] = None

    total_over_0_5: Optional[float] = None
    total_under_0_5: Optional[float] = None
    total_over_1: Optional[float] = None
    total_under_1: Optional[float] = None
    total_over_1_5: Optional[float] = None
    total_under_1_5: Optional[float] = None
    total_over_2: Optional[float] = None
    total_under_2: Optional[float] = None
    total_over_2_5: Optional[float] = None
    total_under_2_5: Optional[float] = None
    total_over_3: Optional[float] = None
    total_under_3: Optional[float] = None
    total_over_3_5: Optional[float] = None
    total_under_3_5: Optional[float] = None
    total_over_4: Optional[float] = None
    total_under_4: Optional[float] = None
    total_over_4_5: Optional[float] = None
    total_under_4_5: Optional[float] = None

    handicap_1_minus_2_5: Optional[float] = None
    handicap_1_minus_2: Optional[float] = None
    handicap_1_minus_1_5: Optional[float] = None
    handicap_1_minus_1: Optional[float] = None
    handicap_1_0: Optional[float] = None
    handicap_1_plus_1: Optional[float] = None
    handicap_1_plus_1_5: Optional[float] = None
    handicap_1_plus_2: Optional[float] = None
    handicap_1_plus_2_5: Optional[float] = None

    handicap_2_minus_2_5: Optional[float] = None
    handicap_2_minus_2: Optional[float] = None
    handicap_2_minus_1_5: Optional[float] = None
    handicap_2_minus_1: Optional[float] = None
    handicap_2_0: Optional[float] = None
    handicap_2_plus_1: Optional[float] = None
    handicap_2_plus_1_5: Optional[float] = None
    handicap_2_plus_2: Optional[float] = None
    handicap_2_plus_2_5: Optional[float] = None

    total_1_over_0_5: Optional[float] = None
    total_1_over_1: Optional[float] = None
    total_1_over_1_5: Optional[float] = None
    total_1_over_2: Optional[float] = None
    total_1_over_2_5: Optional[float] = None
    total_1_under_0_5: Optional[float] = None
    total_1_under_1: Optional[float] = None
    total_1_under_1_5: Optional[float] = None
    total_1_under_2: Optional[float] = None
    total_1_under_2_5: Optional[float] = None

    total_2_over_0_5: Optional[float] = None
    total_2_over_1: Optional[float] = None
    total_2_over_1_5: Optional[float] = None
    total_2_over_2: Optional[float] = None
    total_2_over_2_5: Optional[float] = None
    total_2_under_0_5: Optional[float] = None
    total_2_under_1: Optional[float] = None
    total_2_under_1_5: Optional[float] = None
    total_2_under_2: Optional[float] = None
    total_2_under_2_5: Optional[float] = None


@dataclass
class LeagueInfo:
    name: str
    ru_name: str
    emoji: str
    is_active: bool = False
    squad_id: Optional[int] = None
    xber_url: Optional[str] = None
    fbref_league_id: Optional[int] = None
    fbref_table_url: Optional[str] = None
    fbref_schedule_url: Optional[str] = None
    fbref_playing_time_url: Optional[str] = None
    fbref_standart_url: Optional[str] = None
    fbref_shooting_url: Optional[str] = None
    fbref_passing_url: Optional[str] = None
    fbref_pass_types_url: Optional[str] = None
    fbref_possesion_url: Optional[str] = None
    fbref_shot_creation_url: Optional[str] = None
    sportsmole_name: Optional[str] = None


@dataclass
class TeamLineup:
    team_name: str
    league_name: str
    lineup: str


@dataclass
class LeagueTableInfo:
    team_name: str
    league_name: str
    rank: int
    wins: int
    draws: int
    losses: int
    points: int
    goals_for: int
    goals_against: int
    xg_for: Optional[float] = None
    xg_against: Optional[float] = None


@dataclass
class LeagueScheduleInfo:
    league_name: str
    home_team: str
    away_team: str
    gameweek: int
    date: Optional[date]
    home_goals: Optional[int]
    away_goals: Optional[int]


@dataclass
class CalendarInfo:
    league_name: str
    home_team: str
    away_team: str
    tour: int
    home_points_color: Optional[str]
    away_points_color: Optional[str]
    home_goals_color: Optional[str]
    away_goals_color: Optional[str]
    home_xg_color: Optional[str]
    away_xg_color: Optional[str]


@dataclass
class PlayerStats:
    # common
    name: str
    league_name: str
    team_name: str
    position: str
    # playing time
    games: Optional[int] = None
    minutes: Optional[int] = None
    minutes_per_game: Optional[int] = None
    minutes_pct: Optional[float] = None
    minutes_90s: Optional[float] = None
    games_starts: Optional[int] = None
    minutes_per_start: Optional[int] = None
    games_complete: Optional[int] = None
    games_subs: Optional[int] = None
    minutes_per_sub: Optional[int] = None
    unused_subs: Optional[int] = None
    points_per_game: Optional[float] = None
    on_goals_for: Optional[int] = None
    on_goals_against: Optional[int] = None
    plus_minus: Optional[int] = None
    plus_minus_per90: Optional[float] = None
    plus_minus_wowy: Optional[float] = None
    on_xg_for: Optional[float] = None
    on_xg_against: Optional[float] = None
    xg_plus_minus: Optional[float] = None
    xg_plus_minus_per90: Optional[float] = None
    xg_plus_minus_wowy: Optional[float] = None
    # shooting
    goals: Optional[int] = None
    shots: Optional[int] = None
    shots_on_target: Optional[int] = None
    shots_on_target_pct: Optional[float] = None
    shots_per90: Optional[float] = None
    shots_on_target_per90: Optional[float] = None
    goals_per_shot: Optional[float] = None
    goals_per_shot_on_target: Optional[float] = None
    average_shot_distance: Optional[int] = None
    shots_free_kicks: Optional[int] = None
    pens_made: Optional[int] = None
    pens_att: Optional[int] = None
    xg: Optional[float] = None
    npxg: Optional[float] = None
    xa: Optional[float] = None
    npxg_per_shot: Optional[float] = None
    xg_net: Optional[float] = None
    npxg_net: Optional[float] = None
    # passing
    passes_completed: Optional[int] = None
    passes: Optional[int] = None
    passes_pct: Optional[float] = None
    passes_total_distance: Optional[int] = None
    passes_progressive_distance: Optional[int] = None
    passes_short: Optional[int] = None
    passes_completed_short: Optional[int] = None
    passes_pct_short: Optional[float] = None
    passes_medium: Optional[int] = None
    passes_completed_medium: Optional[int] = None
    passes_pct_medium: Optional[float] = None
    passes_long: Optional[int] = None
    passes_completed_long: Optional[int] = None
    passes_pct_long: Optional[float] = None
    assists: Optional[int] = None
    xg_assist: Optional[float] = None
    pass_xa: Optional[float] = None
    xg_assist_net: Optional[float] = None
    assisted_shots: Optional[int] = None
    passes_into_final_third: Optional[int] = None
    passes_into_penalty_area: Optional[int] = None
    crosses_into_penalty_area: Optional[int] = None
    progressive_passes: Optional[int] = None
    # pass types
    passes_live: Optional[int] = None
    passes_dead: Optional[int] = None
    passes_free_kicks: Optional[int] = None
    through_balls: Optional[int] = None
    passes_switches: Optional[int] = None
    crosses: Optional[int] = None
    throw_ins: Optional[int] = None
    corner_kicks: Optional[int] = None
    corner_kicks_in: Optional[int] = None
    corner_kicks_out: Optional[int] = None
    corner_kicks_straight: Optional[int] = None
    passes_offsides: Optional[int] = None
    passes_blocked: Optional[int] = None
    # possesion
    touches: Optional[int] = None
    touches_def_pen_area: Optional[int] = None
    touches_def_3rd: Optional[int] = None
    touches_mid_3rd: Optional[int] = None
    touches_att_3rd: Optional[int] = None
    touches_att_pen_area: Optional[int] = None
    touches_live_ball: Optional[int] = None
    take_ons: Optional[int] = None
    take_ons_won: Optional[int] = None
    take_ons_won_pct: Optional[float] = None
    take_ons_tackled: Optional[int] = None
    take_ons_tackled_pct: Optional[float] = None
    carries: Optional[int] = None
    carries_distance: Optional[int] = None
    carries_progressive_distance: Optional[int] = None
    progressive_carries: Optional[int] = None
    carries_into_final_third: Optional[int] = None
    carries_into_penalty_area: Optional[int] = None
    miscontrols: Optional[int] = None
    dispossessed: Optional[int] = None
    passes_received: Optional[int] = None
    progressive_passes_received: Optional[int] = None
    # shot creation
    sca: Optional[int] = None
    sca_per90: Optional[float] = None
    sca_passes_live: Optional[int] = None
    sca_passes_dead: Optional[int] = None
    sca_take_ons: Optional[int] = None
    sca_shots: Optional[int] = None
    sca_fouled: Optional[int] = None
    sca_defense: Optional[int] = None
    gca: Optional[int] = None
    gca_per90: Optional[float] = None
    gca_passes_live: Optional[int] = None
    gca_passes_dead: Optional[int] = None
    gca_take_ons: Optional[int] = None
    gca_shots: Optional[int] = None
    gca_fouled: Optional[int] = None
    gca_defense: Optional[int] = None
    # cards
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None


@dataclass
class PlayerStatsInfo:
    name: Optional[str] = None
    team: Optional[str] = None
    position: Optional[str] = None
    # playing time
    games: Optional[int] = None
    minutes: Optional[int] = None
    # shooting
    goals: Optional[int] = None
    shots: Optional[int] = None
    shots_on_target: Optional[int] = None
    average_shot_distance: Optional[float] = None
    xg: Optional[float] = None
    xg_np: Optional[float] = None
    xg_xa: Optional[float] = None
    xg_np_xa: Optional[float] = None
    # passing
    assists: Optional[int] = None
    xa: Optional[float] = None
    key_passes: Optional[int] = None
    passes_into_penalty_area: Optional[int] = None
    crosses_into_penalty_area: Optional[int] = None
    # possesion
    touches_in_attacking_third: Optional[int] = None
    touches_in_attacking_penalty_area: Optional[int] = None
    carries_in_attacking_third: Optional[int] = None
    carries_in_attacking_penalty_area: Optional[int] = None
    # shot creation
    sca: Optional[int] = None
    gca: Optional[int] = None
    # sports info
    sports_name: Optional[str] = None
    sports_team: Optional[str] = None
    role: Optional[str] = None
    price: Optional[float] = None
    percent_ownership: Optional[float] = None
    percent_ownership_diff: Optional[float] = None


@dataclass
class PlayersStatsDiff:
    titles: List[str]
    left_bars: List[float]
    right_bars: List[float]
    left_abs_values: List[float]
    right_abs_values: List[float]


@dataclass
class FreeKicksInfo:
    name: str
    team: Optional[str] = None
    position: Optional[str] = None
    # playing time
    games: Optional[int] = None
    # pass types
    corner_kicks: Optional[float] = None
    # shooting
    penalty_goals: Optional[float] = None  # pens_made
    penalty_shots: Optional[float] = None  # pens_att
    free_kicks_shots: Optional[float] = None  # shots_free_kicks
    # sports info
    sports_name: Optional[str] = None
    sports_team: Optional[str] = None
    role: Optional[str] = None
    price: Optional[float] = None
    percent_ownership: Optional[float] = None
    percent_ownership_diff: Optional[float] = None


@dataclass
class SportsPlayerStats:
    sports_id: int
    name: str
    league_name: str
    tour: Optional[int] = None
    role: Optional[str] = None
    price: Optional[float] = None
    percent_ownership: Optional[float] = None
    team_name: Optional[str] = None
    place: Optional[int] = None
    score: Optional[int] = None
    average_score: Optional[float] = None
    goals: Optional[int] = None
    assists: Optional[int] = None
    goals_conceded: Optional[int] = None
    yellow_cards: Optional[int] = None
    red_cards: Optional[int] = None
    field_minutes: Optional[int] = None
    saves: Optional[int] = None


@dataclass
class SportsPlayerDiff:
    name: str
    league_name: str
    team_name: Optional[str] = None
    role: Optional[str] = None
    price: Optional[float] = None
    percent_ownership: Optional[float] = None
    percent_ownership_diff: Optional[float] = None


@dataclass
class SportsMatchInfo:
    id: int
    match_status: str
    scheduled_at_stamp: int
    date_only: bool
    home_team: Optional[str] = None
    away_team: Optional[str] = None
    scheduled_at_datetime: Optional[datetime] = None
    tour_number: Optional[int] = None


@dataclass
class SportsTourInfo:
    league_name: str
    number: int
    matches: List[SportsMatchInfo]
    deadline: datetime
    status: str


@dataclass
class TeamName:
    league_name: Optional[str] = None
    sports_name: Optional[str] = None
    fbref_name: Optional[str] = None
    xbet_name: Optional[str] = None
    name: Optional[str] = None

    def __post_init__(self):
        if self.name is None:
            if self.sports_name is not None:
                self.name = self.sports_name
            elif self.xbet_name is not None:
                self.name = self.xbet_name
            else:
                self.name = self.fbref_name

    def __hash__(self):
        return hash((self.league_name, self.sports_name, self.fbref_name, self.xbet_name, self.name))


@dataclass
class PlayerName:
    league_name: Optional[str] = None
    team_name: Optional[str] = None
    sports_name: Optional[str] = None
    fbref_name: Optional[str] = None
    name: Optional[str] = None

    def __post_init__(self):
        if self.name is None:
            if self.sports_name is not None:
                self.name = self.sports_name
            else:
                self.name = self.fbref_name

    def __hash__(self):
        return hash((self.league_name, self.team_name, self.sports_name, self.fbref_name, self.name))


@dataclass
class PlayersLeagueStats:
    abs_stats: Optional[pd.DataFrame] = None
    norm_stats: Optional[pd.DataFrame] = None
    free_kicks: Optional[pd.DataFrame] = None

    def to_json(self) -> Dict:
        """
        Converts the instance variables to a JSON object.

        Returns:
            Dict: A dictionary representing the JSON data.
        """
        return {
            "abs_stats": self.abs_stats.to_json(),
            "norm_stats": self.norm_stats.to_json(),
            "free_kicks": self.free_kicks.to_json(),
        }

    def from_json(self, json_data: Dict) -> None:
        """
        Parses a JSON object and assigns the parsed data to instance variables.

        Args:
            json_data (Dict): A dictionary representing the JSON data to be parsed.

        Returns:
            None
        """
        self.abs_stats = pd.read_json(json_data["abs_stats"])
        self.norm_stats = pd.read_json(json_data["norm_stats"])
        self.free_kicks = pd.read_json(json_data["free_kicks"])
