from datetime import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Float

from fantasy_helper.db.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True)
    name = Column(String, primary_key=False)
    league_name = Column(String, nullable=False)
    team_name = Column(String, nullable=False)
    position = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    # playing time
    games = Column(Integer, nullable=True)
    minutes = Column(Integer, nullable=True)
    minutes_per_game = Column(Integer, nullable=True)
    minutes_pct = Column(Float, nullable=True)
    minutes_90s = Column(Float, nullable=True)
    games_starts = Column(Integer, nullable=True)
    minutes_per_start = Column(Integer, nullable=True)
    games_complete = Column(Integer, nullable=True)
    games_subs = Column(Integer, nullable=True)
    minutes_per_sub = Column(Integer, nullable=True)
    unused_subs = Column(Integer, nullable=True)
    points_per_game = Column(Float, nullable=True)
    on_goals_for = Column(Integer, nullable=True)
    on_goals_against = Column(Integer, nullable=True)
    plus_minus = Column(Integer, nullable=True)
    plus_minus_per90 = Column(Float, nullable=True)
    plus_minus_wowy = Column(Float, nullable=True)
    on_xg_for = Column(Float, nullable=True)
    on_xg_against = Column(Float, nullable=True)
    xg_plus_minus = Column(Float, nullable=True)
    xg_plus_minus_per90 = Column(Float, nullable=True)
    xg_plus_minus_wowy = Column(Float, nullable=True)
    # shooting
    goals = Column(Integer, nullable=True)
    shots = Column(Integer, nullable=True)
    shots_on_target = Column(Integer, nullable=True)
    shots_on_target_pct = Column(Float, nullable=True)
    shots_per90 = Column(Float, nullable=True)
    shots_on_target_per90 = Column(Float, nullable=True)
    goals_per_shot = Column(Float, nullable=True)
    goals_per_shot_on_target = Column(Float, nullable=True)
    average_shot_distance = Column(Integer, nullable=True)
    shots_free_kicks = Column(Integer, nullable=True)
    pens_made = Column(Integer, nullable=True)
    pens_att = Column(Integer, nullable=True)
    xg = Column(Float, nullable=True)
    npxg = Column(Float, nullable=True)
    xa = Column(Float, nullable=True)
    npxg_per_shot = Column(Float, nullable=True)
    xg_net = Column(Float, nullable=True)
    npxg_net = Column(Float, nullable=True)
    # passing
    passes_completed = Column(Integer, nullable=True)
    passes = Column(Integer, nullable=True)
    passes_pct = Column(Float, nullable=True)
    passes_total_distance = Column(Integer, nullable=True)
    passes_progressive_distance = Column(Integer, nullable=True)
    passes_short = Column(Integer, nullable=True)
    passes_completed_short = Column(Integer, nullable=True)
    passes_pct_short = Column(Float, nullable=True)
    passes_medium = Column(Integer, nullable=True)
    passes_completed_medium = Column(Integer, nullable=True)
    passes_pct_medium = Column(Float, nullable=True)
    passes_long = Column(Integer, nullable=True)
    passes_completed_long = Column(Integer, nullable=True)
    passes_pct_long = Column(Float, nullable=True)
    assists = Column(Integer, nullable=True)
    xg_assist = Column(Float, nullable=True)
    pass_xa = Column(Float, nullable=True)
    xg_assist_net = Column(Float, nullable=True)
    assisted_shots = Column(Integer, nullable=True)
    passes_into_final_third = Column(Integer, nullable=True)
    passes_into_penalty_area = Column(Integer, nullable=True)
    crosses_into_penalty_area = Column(Integer, nullable=True)
    progressive_passes = Column(Integer, nullable=True)
    # pass types
    passes_live = Column(Integer, nullable=True)
    passes_dead = Column(Integer, nullable=True)
    passes_free_kicks = Column(Integer, nullable=True)
    through_balls = Column(Integer, nullable=True)
    passes_switches = Column(Integer, nullable=True)
    crosses = Column(Integer, nullable=True)
    throw_ins = Column(Integer, nullable=True)
    corner_kicks = Column(Integer, nullable=True)
    corner_kicks_in = Column(Integer, nullable=True)
    corner_kicks_out = Column(Integer, nullable=True)
    corner_kicks_straight = Column(Integer, nullable=True)
    passes_offsides = Column(Integer, nullable=True)
    passes_blocked = Column(Integer, nullable=True)
    # possession
    touches = Column(Integer, nullable=True)
    touches_def_pen_area = Column(Integer, nullable=True)
    touches_def_3rd = Column(Integer, nullable=True)
    touches_mid_3rd = Column(Integer, nullable=True)
    touches_att_3rd = Column(Integer, nullable=True)
    touches_att_pen_area = Column(Integer, nullable=True)
    touches_live_ball = Column(Integer, nullable=True)
    take_ons = Column(Integer, nullable=True)
    take_ons_won = Column(Integer, nullable=True)
    take_ons_won_pct = Column(Float, nullable=True)
    take_ons_tackled = Column(Integer, nullable=True)
    take_ons_tackled_pct = Column(Float, nullable=True)
    carries = Column(Integer, nullable=True)
    carries_distance = Column(Integer, nullable=True)
    carries_progressive_distance = Column(Integer, nullable=True)
    progressive_carries = Column(Integer, nullable=True)
    carries_into_final_third = Column(Integer, nullable=True)
    carries_into_penalty_area = Column(Integer, nullable=True)
    miscontrols = Column(Integer, nullable=True)
    dispossessed = Column(Integer, nullable=True)
    passes_received = Column(Integer, nullable=True)
    progressive_passes_received = Column(Integer, nullable=True)
    # shot creation
    sca = Column(Integer, nullable=True)
    sca_per90 = Column(Float, nullable=True)
    sca_passes_live = Column(Integer, nullable=True)
    sca_passes_dead = Column(Integer, nullable=True)
    sca_take_ons = Column(Integer, nullable=True)
    sca_shots = Column(Integer, nullable=True)
    sca_fouled = Column(Integer, nullable=True)
    sca_defense = Column(Integer, nullable=True)
    gca = Column(Integer, nullable=True)
    gca_per90 = Column(Float, nullable=True)
    gca_passes_live = Column(Integer, nullable=True)
    gca_passes_dead = Column(Integer, nullable=True)
    gca_take_ons = Column(Integer, nullable=True)
    gca_shots = Column(Integer, nullable=True)
    gca_fouled = Column(Integer, nullable=True)
    gca_defense = Column(Integer, nullable=True)
    # cards
    yellow_cards = Column(Integer, nullable=True)
    red_cards = Column(Integer, nullable=True)

    def __init__(
        self,
        name: str,
        league_name: str,
        team_name: str,
        position: str,
        timestamp: datetime,
        # playing time
        games: Optional[int],
        minutes: Optional[int],
        minutes_per_game: Optional[int],
        minutes_pct: Optional[float],
        minutes_90s: Optional[float],
        games_starts: Optional[int],
        minutes_per_start: Optional[int],
        games_complete: Optional[int],
        games_subs: Optional[int],
        minutes_per_sub: Optional[int],
        unused_subs: Optional[int],
        points_per_game: Optional[float],
        on_goals_for: Optional[int],
        on_goals_against: Optional[int],
        plus_minus: Optional[int],
        plus_minus_per90: Optional[float],
        plus_minus_wowy: Optional[float],
        on_xg_for: Optional[float],
        on_xg_against: Optional[float],
        xg_plus_minus: Optional[float],
        xg_plus_minus_per90: Optional[float],
        xg_plus_minus_wowy: Optional[float],
        # shooting
        goals: Optional[int],
        shots: Optional[int],
        shots_on_target: Optional[int],
        shots_on_target_pct: Optional[float],
        shots_per90: Optional[float],
        shots_on_target_per90: Optional[float],
        goals_per_shot: Optional[float],
        goals_per_shot_on_target: Optional[float],
        average_shot_distance: Optional[int],
        shots_free_kicks: Optional[int],
        pens_made: Optional[int],
        pens_att: Optional[int],
        xg: Optional[float],
        npxg: Optional[float],
        xa: Optional[float],
        npxg_per_shot: Optional[float],
        xg_net: Optional[float],
        npxg_net: Optional[float],
        # passing
        passes_completed: Optional[int],
        passes: Optional[int],
        passes_pct: Optional[float],
        passes_total_distance: Optional[int],
        passes_progressive_distance: Optional[int],
        passes_short: Optional[int],
        passes_completed_short: Optional[int],
        passes_pct_short: Optional[float],
        passes_medium: Optional[int],
        passes_completed_medium: Optional[int],
        passes_pct_medium: Optional[float],
        passes_long: Optional[int],
        passes_completed_long: Optional[int],
        passes_pct_long: Optional[float],
        assists: Optional[int],
        xg_assist: Optional[float],
        pass_xa: Optional[float],
        xg_assist_net: Optional[float],
        assisted_shots: Optional[int],
        passes_into_final_third: Optional[int],
        passes_into_penalty_area: Optional[int],
        crosses_into_penalty_area: Optional[int],
        progressive_passes: Optional[int],
        # pass types
        passes_live: Optional[int],
        passes_dead: Optional[int],
        passes_free_kicks: Optional[int],
        through_balls: Optional[int],
        passes_switches: Optional[int],
        crosses: Optional[int],
        throw_ins: Optional[int],
        corner_kicks: Optional[int],
        corner_kicks_in: Optional[int],
        corner_kicks_out: Optional[int],
        corner_kicks_straight: Optional[int],
        passes_offsides: Optional[int],
        passes_blocked: Optional[int],
        # possession
        touches: Optional[int],
        touches_def_pen_area: Optional[int],
        touches_def_3rd: Optional[int],
        touches_mid_3rd: Optional[int],
        touches_att_3rd: Optional[int],
        touches_att_pen_area: Optional[int],
        touches_live_ball: Optional[int],
        take_ons: Optional[int],
        take_ons_won: Optional[int],
        take_ons_won_pct: Optional[float],
        take_ons_tackled: Optional[int],
        take_ons_tackled_pct: Optional[float],
        carries: Optional[int],
        carries_distance: Optional[int],
        carries_progressive_distance: Optional[int],
        progressive_carries: Optional[int],
        carries_into_final_third: Optional[int],
        carries_into_penalty_area: Optional[int],
        miscontrols: Optional[int],
        dispossessed: Optional[int],
        passes_received: Optional[int],
        progressive_passes_received: Optional[int],
        # shot creation
        sca: Optional[int],
        sca_per90: Optional[float],
        sca_passes_live: Optional[int],
        sca_passes_dead: Optional[int],
        sca_take_ons: Optional[int],
        sca_shots: Optional[int],
        sca_fouled: Optional[int],
        sca_defense: Optional[int],
        gca: Optional[int],
        gca_per90: Optional[float],
        gca_passes_live: Optional[int],
        gca_passes_dead: Optional[int],
        gca_take_ons: Optional[int],
        gca_shots: Optional[int],
        gca_fouled: Optional[int],
        gca_defense: Optional[int],
        # cards
        yellow_cards: Optional[int],
        red_cards: Optional[int],
    ):
        self.name = name
        self.league_name = league_name
        self.team_name = team_name
        self.position = position
        self.timestamp = timestamp
        # playing time
        self.games = games
        self.minutes = minutes
        self.minutes_per_game = minutes_per_game
        self.minutes_pct = minutes_pct
        self.minutes_90s = minutes_90s
        self.games_starts = games_starts
        self.minutes_per_start = minutes_per_start
        self.games_complete = games_complete
        self.games_subs = games_subs
        self.minutes_per_sub = minutes_per_sub
        self.unused_subs = unused_subs
        self.points_per_game = points_per_game
        self.on_goals_for = on_goals_for
        self.on_goals_against = on_goals_against
        self.plus_minus = plus_minus
        self.plus_minus_per90 = plus_minus_per90
        self.plus_minus_wowy = plus_minus_wowy
        self.on_xg_for = on_xg_for
        self.on_xg_against = on_xg_against
        self.xg_plus_minus = xg_plus_minus
        self.xg_plus_minus_per90 = xg_plus_minus_per90
        self.xg_plus_minus_wowy = xg_plus_minus_wowy
        # shooting
        self.goals = goals
        self.shots = shots
        self.shots_on_target = shots_on_target
        self.shots_on_target_pct = shots_on_target_pct
        self.shots_per90 = shots_per90
        self.shots_on_target_per90 = shots_on_target_per90
        self.goals_per_shot = goals_per_shot
        self.goals_per_shot_on_target = goals_per_shot_on_target
        self.average_shot_distance = average_shot_distance
        self.shots_free_kicks = shots_free_kicks
        self.pens_made = pens_made
        self.pens_att = pens_att
        self.xg = xg
        self.npxg = npxg
        self.xa = xa
        self.npxg_per_shot = npxg_per_shot
        self.xg_net = xg_net
        self.npxg_net = npxg_net
        # passing
        self.passes_completed = passes_completed
        self.passes = passes
        self.passes_pct = passes_pct
        self.passes_total_distance = passes_total_distance
        self.passes_progressive_distance = passes_progressive_distance
        self.passes_short = passes_short
        self.passes_completed_short = passes_completed_short
        self.passes_pct_short = passes_pct_short
        self.passes_medium = passes_medium
        self.passes_completed_medium = passes_completed_medium
        self.passes_pct_medium = passes_pct_medium
        self.passes_long = passes_long
        self.passes_completed_long = passes_completed_long
        self.passes_pct_long = passes_pct_long
        self.assists = assists
        self.xg_assist = xg_assist
        self.pass_xa = pass_xa
        self.xg_assist_net = xg_assist_net
        self.assisted_shots = assisted_shots
        self.passes_into_final_third = passes_into_final_third
        self.passes_into_penalty_area = passes_into_penalty_area
        self.crosses_into_penalty_area = crosses_into_penalty_area
        self.progressive_passes = progressive_passes
        # pass types
        self.passes_live = passes_live
        self.passes_dead = passes_dead
        self.passes_free_kicks = passes_free_kicks
        self.through_balls = through_balls
        self.passes_switches = passes_switches
        self.crosses = crosses
        self.throw_ins = throw_ins
        self.corner_kicks = corner_kicks
        self.corner_kicks_in = corner_kicks_in
        self.corner_kicks_out = corner_kicks_out
        self.corner_kicks_straight = corner_kicks_straight
        self.passes_offsides = passes_offsides
        self.passes_blocked = passes_blocked
        # possession
        self.touches = touches
        self.touches_def_pen_area = touches_def_pen_area
        self.touches_def_3rd = touches_def_3rd
        self.touches_mid_3rd = touches_mid_3rd
        self.touches_att_3rd = touches_att_3rd
        self.touches_att_pen_area = touches_att_pen_area
        self.touches_live_ball = touches_live_ball
        self.take_ons = take_ons
        self.take_ons_won = take_ons_won
        self.take_ons_won_pct = take_ons_won_pct
        self.take_ons_tackled = take_ons_tackled
        self.take_ons_tackled_pct = take_ons_tackled_pct
        self.carries = carries
        self.carries_distance = carries_distance
        self.carries_progressive_distance = carries_progressive_distance
        self.progressive_carries = progressive_carries
        self.carries_into_final_third = carries_into_final_third
        self.carries_into_penalty_area = carries_into_penalty_area
        self.miscontrols = miscontrols
        self.dispossessed = dispossessed
        self.passes_received = passes_received
        self.progressive_passes_received = progressive_passes_received
        # shot creation
        self.sca = sca
        self.sca_per90 = sca_per90
        self.sca_passes_live = sca_passes_live
        self.sca_passes_dead = sca_passes_dead
        self.sca_take_ons = sca_take_ons
        self.sca_shots = sca_shots
        self.sca_fouled = sca_fouled
        self.sca_defense = sca_defense
        self.gca = gca
        self.gca_per90 = gca_per90
        self.gca_passes_live = gca_passes_live
        self.gca_passes_dead = gca_passes_dead
        self.gca_take_ons = gca_take_ons
        self.gca_shots = gca_shots
        self.gca_fouled = gca_fouled
        self.gca_defense = gca_defense
        # cards
        self.yellow_cards = yellow_cards
        self.red_cards = red_cards
        
    def __repr__(self):
        return f"{self.name} [{self.position}] from {self.team_name}"
