import datetime
from typing import Optional

from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime, Float, Date

from fantasy_helper.db.database import Base


class PlayersMatch(Base):
    __tablename__ = "players_matches"

    id = Column(Integer, primary_key=True)
    # common
    name = Column(String, primary_key=False)
    player_id = Column(String, nullable=False, index=True)
    league_name = Column(String, nullable=False, index=True)
    team_name = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False)
    minutes = Column(Integer, nullable=True)
    player_url = Column(String, nullable=True)
    shirt_number = Column(Integer, nullable=True)
    position = Column(String, nullable=True)
    nationality = Column(String, nullable=True)
    # match info
    home_team = Column(String, nullable=True)
    away_team = Column(String, nullable=True)
    gameweek = Column(Integer, nullable=True)
    date = Column(Date, nullable=True)
    match_url = Column(String, nullable=True)
    # summary
    goals = Column(Integer, nullable=True)
    pens_made = Column(Integer, nullable=True)
    pens_att = Column(Integer, nullable=True)
    shots = Column(Integer, nullable=True)
    shots_on_target = Column(Integer, nullable=True)
    xg = Column(Float, nullable=True)
    xg_np = Column(Float, nullable=True)
    sca = Column(Float, nullable=True)
    gca = Column(Float, nullable=True)
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
    # defensive actions
    tackles = Column(Integer, nullable=True)
    tackles_won = Column(Integer, nullable=True)
    tackles_def_3rd = Column(Integer, nullable=True)
    tackles_mid_3rd = Column(Integer, nullable=True)
    tackles_att_3rd = Column(Integer, nullable=True)
    challenge_tackles = Column(Integer, nullable=True)
    challenges = Column(Integer, nullable=True)
    challenge_tackles_pct = Column(Float, nullable=True)
    challenges_lost = Column(Integer, nullable=True)
    blocks = Column(Integer, nullable=True)
    blocked_shots = Column(Integer, nullable=True)
    blocked_passes = Column(Integer, nullable=True)
    interceptions = Column(Integer, nullable=True)
    tackles_interceptions = Column(Integer, nullable=True)
    clearances = Column(Integer, nullable=True)
    errors = Column(Integer, nullable=True)
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
    # miscellaneous
    yellow_cards = Column(Integer, nullable=True)
    red_cards = Column(Integer, nullable=True)
    yellow_red_cards = Column(Integer, nullable=True)
    fouls = Column(Integer, nullable=True)
    fouled = Column(Integer, nullable=True)
    offsides = Column(Integer, nullable=True)
    pens_won = Column(Integer, nullable=True)
    pens_conceded = Column(Integer, nullable=True)
    own_goals = Column(Integer, nullable=True)
    ball_recoveries = Column(Integer, nullable=True)
    aerials_won = Column(Integer, nullable=True)
    aerials_lost = Column(Integer, nullable=True)
    aerials_won_pct = Column(Float, nullable=True)
    # goalkeeping
    gk_shots_on_target_against = Column(Integer, nullable=True)
    gk_goals_against = Column(Integer, nullable=True)
    gk_saves = Column(Integer, nullable=True)
    gk_save_pct = Column(Float, nullable=True)
    gk_psxg = Column(Float, nullable=True)
    gk_passes_completed_launched = Column(Integer, nullable=True)
    gk_passes_launched = Column(Integer, nullable=True)
    gk_passes_pct_launched = Column(Float, nullable=True)
    gk_passes = Column(Integer, nullable=True)
    gk_passes_throws = Column(Integer, nullable=True)
    gk_pct_passes_launched = Column(Float, nullable=True)
    gk_passes_length_avg = Column(Float, nullable=True)
    gk_goal_kicks = Column(Integer, nullable=True)
    gk_pct_goal_kicks_launched = Column(Float, nullable=True)
    gk_goal_kick_length_avg = Column(Float, nullable=True)
    gk_crosses = Column(Integer, nullable=True)
    gk_crosses_stopped = Column(Integer, nullable=True)
    gk_crosses_stopped_pct = Column(Float, nullable=True)
    gk_def_actions_outside_pen_area = Column(Integer, nullable=True)
    gk_avg_distance_def_actions = Column(Float, nullable=True)
    year = Column(String, nullable=True, default="2024")

    def __init__(
        self,
        # common
        name: str,
        player_id: str,
        league_name: str,
        team_name: str,
        timestamp: datetime.datetime,
        minutes: Optional[int],
        player_url: Optional[str],
        shirt_number: Optional[int],
        position: Optional[str],
        nationality: Optional[str],
        # match info
        home_team: Optional[str],
        away_team: Optional[str],
        gameweek: Optional[int],
        date: Optional[datetime.date],
        match_url: Optional[str],
        # summary
        goals: Optional[int],
        pens_made: Optional[int],
        pens_att: Optional[int],
        shots: Optional[int],
        shots_on_target: Optional[int],
        xg: Optional[float],
        xg_np: Optional[float],
        sca: Optional[float],
        gca: Optional[float],
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
        # defensive actions
        tackles: Optional[int],
        tackles_won: Optional[int],
        tackles_def_3rd: Optional[int],
        tackles_mid_3rd: Optional[int],
        tackles_att_3rd: Optional[int],
        challenge_tackles: Optional[int],
        challenges: Optional[int],
        challenge_tackles_pct: Optional[float],
        challenges_lost: Optional[int],
        blocks: Optional[int],
        blocked_shots: Optional[int],
        blocked_passes: Optional[int],
        interceptions: Optional[int],
        tackles_interceptions: Optional[int],
        clearances: Optional[int],
        errors: Optional[int],
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
        # miscellaneous
        yellow_cards: Optional[int],
        red_cards: Optional[int],
        yellow_red_cards: Optional[int],
        fouls: Optional[int],
        fouled: Optional[int],
        offsides: Optional[int],
        pens_won: Optional[int],
        pens_conceded: Optional[int],
        own_goals: Optional[int],
        ball_recoveries: Optional[int],
        aerials_won: Optional[int],
        aerials_lost: Optional[int],
        aerials_won_pct: Optional[float],
        # goalkeeping
        gk_shots_on_target_against: Optional[int],
        gk_goals_against: Optional[int],
        gk_saves: Optional[int],
        gk_save_pct: Optional[float],
        gk_psxg: Optional[float],
        gk_passes_completed_launched: Optional[int],
        gk_passes_launched: Optional[int],
        gk_passes_pct_launched: Optional[float],
        gk_passes: Optional[int],
        gk_passes_throws: Optional[int],
        gk_pct_passes_launched: Optional[float],
        gk_passes_length_avg: Optional[float],
        gk_goal_kicks: Optional[int],
        gk_pct_goal_kicks_launched: Optional[float],
        gk_goal_kick_length_avg: Optional[float],
        gk_crosses: Optional[int],
        gk_crosses_stopped: Optional[int],
        gk_crosses_stopped_pct: Optional[float],
        gk_def_actions_outside_pen_area: Optional[int],
        gk_avg_distance_def_actions: Optional[float],
        year: str = "2024",
    ):
        self.name = name
        self.player_id = player_id
        self.league_name = league_name
        self.team_name = team_name
        self.timestamp = timestamp
        self.minutes = minutes
        self.player_url = player_url
        self.shirt_number = shirt_number
        self.position = position
        self.nationality = nationality
        # match info
        self.home_team = home_team
        self.away_team = away_team
        self.gameweek = gameweek
        self.date = date
        self.match_url = match_url
        # summary
        self.goals = goals
        self.pens_made = pens_made
        self.pens_att = pens_att
        self.shots = shots
        self.shots_on_target = shots_on_target
        self.xg = xg
        self.xg_np = xg_np
        self.sca = sca
        self.gca = gca
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
        # defensive actions
        self.tackles = tackles
        self.tackles_won = tackles_won
        self.tackles_def_3rd = tackles_def_3rd
        self.tackles_mid_3rd = tackles_mid_3rd
        self.tackles_att_3rd = tackles_att_3rd
        self.challenge_tackles = challenge_tackles
        self.challenges = challenges
        self.challenge_tackles_pct = challenge_tackles_pct
        self.challenges_lost = challenges_lost
        self.blocks = blocks
        self.blocked_shots = blocked_shots
        self.blocked_passes = blocked_passes
        self.interceptions = interceptions
        self.tackles_interceptions = tackles_interceptions
        self.clearances = clearances
        self.errors = errors
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
        # miscellaneous
        self.yellow_cards = yellow_cards
        self.red_cards = red_cards
        self.yellow_red_cards = yellow_red_cards
        self.fouls = fouls
        self.fouled = fouled
        self.offsides = offsides
        self.pens_won = pens_won
        self.pens_conceded = pens_conceded
        self.own_goals = own_goals
        self.ball_recoveries = ball_recoveries
        self.aerials_won = aerials_won
        self.aerials_lost = aerials_lost
        self.aerials_won_pct = aerials_won_pct
        # goalkeeping
        self.gk_shots_on_target_against = gk_shots_on_target_against
        self.gk_goals_against = gk_goals_against
        self.gk_saves = gk_saves
        self.gk_save_pct = gk_save_pct
        self.gk_psxg = gk_psxg
        self.gk_passes_completed_launched = gk_passes_completed_launched
        self.gk_passes_launched = gk_passes_launched
        self.gk_passes_pct_launched = gk_passes_pct_launched
        self.gk_passes = gk_passes
        self.gk_passes_throws = gk_passes_throws
        self.gk_pct_passes_launched = gk_pct_passes_launched
        self.gk_passes_length_avg = gk_passes_length_avg
        self.gk_goal_kicks = gk_goal_kicks
        self.gk_pct_goal_kicks_launched = gk_pct_goal_kicks_launched
        self.gk_goal_kick_length_avg = gk_goal_kick_length_avg
        self.gk_crosses = gk_crosses
        self.gk_crosses_stopped = gk_crosses_stopped
        self.gk_crosses_stopped_pct = gk_crosses_stopped_pct
        self.gk_def_actions_outside_pen_area = gk_def_actions_outside_pen_area
        self.gk_avg_distance_def_actions = gk_avg_distance_def_actions
        self.year = year
        
    def __repr__(self):
        return f"{self.name} [{self.position}] from {self.team_name}"
