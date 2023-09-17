from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class MatchInfo:
    url: str
    league_name: str
    home_team: str
    away_team: str
    start_datetime: Optional[datetime] = None
    total_1_over_1_5: Optional[float] = None
    total_1_under_0_5: Optional[float] = None
    total_2_over_1_5: Optional[float] = None
    total_2_under_0_5: Optional[float] = None


@dataclass
class LeagueInfo:
    name: str
    ru_name: str
    emoji: str
    squad_id: Optional[int] = None
    xber_url: Optional[str] = None
    fbref_playing_time_url: Optional[str] = None
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


@dataclass
class PlayerStatsInfo:
    name: str
    team: Optional[str] = None
    position: Optional[str] = None
    # playing time
    games: Optional[int] = None
    minutes: Optional[int] = None
    # shooting
    goals: Optional[float] = None
    shots: Optional[float] = None
    shots_on_target: Optional[float] = None
    xg: Optional[float] = None
    xg_np: Optional[float] = None
    # passing
    xa: Optional[float] = None
    key_passes: Optional[float] = None
    passes_into_penalty_area: Optional[float] = None
    crosses_into_penalty_area: Optional[float] = None
    # possesion
    touches_in_attacking_third: Optional[float] = None
    touches_in_attacking_penalty_area: Optional[float] = None
    carries_in_attacking_third: Optional[float] = None
    carries_in_attacking_penalty_area: Optional[float] = None


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
