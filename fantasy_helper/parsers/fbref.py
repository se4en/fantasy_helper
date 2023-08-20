import logging
import os
import sys
from dataclasses import asdict
from typing import Any, Callable, Dict, Optional, List, Tuple

import requests
from bs4 import BeautifulSoup

from fantasy_helper.utils.dataclasses import LeagueInfo, PlayerStats


class FbrefParser:
    def __init__(self, leagues: List[LeagueInfo]):
        self.__playing_time_leagues = {
            l.name: l.fbref_playing_time_url
            for l in leagues
            if l.fbref_playing_time_url is not None
        }
        self.__shooting_leagues = {
            l.name: l.fbref_shooting_url
            for l in leagues
            if l.fbref_shooting_url is not None
        }
        self.__passing_leagues = {
            l.name: l.fbref_passing_url
            for l in leagues
            if l.fbref_passing_url is not None
        }
        self.__pass_types_leagues = {
            l.name: l.fbref_pass_types_url
            for l in leagues
            if l.fbref_pass_types_url is not None
        }
        self.__possession_leagues = {
            l.name: l.fbref_possesion_url
            for l in leagues
            if l.fbref_possesion_url is not None
        }
        self.__shot_creation_leagues = {
            l.name: l.fbref_shot_creation_url
            for l in leagues
            if l.fbref_shot_creation_url is not None
        }

    def __parse_player_shooting_stat(
        self, player: Any, league_name: str
    ) -> Optional[PlayerStats]:
        if player.find("td", {"data-stat": "player"}) is not None:
            # shots
            _goals = player.find("td", {"data-stat": "goals"})
            _shots = player.find("td", {"data-stat": "shots"})
            _shots_on_target = player.find("td", {"data-stat": "shots_on_target"})
            _shots_on_target_pct = player.find(
                "td", {"data-stat": "shots_on_target_pct"}
            )
            _shots_per90 = player.find("td", {"data-stat": "shots_per_90"})
            _shots_on_target_per90 = player.find(
                "td", {"data-stat": "shots_on_target_per90"}
            )
            _goals_per_shot = player.find("td", {"data-stat": "goals_per_shot"})
            _goals_per_shot_on_target = player.find(
                "td", {"data-stat": "goals_per_shot_on_target"}
            )
            _average_shot_distance = player.find(
                "td", {"data-stat": "average_shot_distance"}
            )
            _shots_free_kicks = player.find("td", {"data-stat": "shots_free_kicks"})
            _pens_made = player.find("td", {"data-stat": "pens_made"})
            _pens_att = player.find("td", {"data-stat": "pens_att"})
            # xg
            _xg = player.find("td", {"data-stat": "xg"})
            _npxg = player.find("td", {"data-stat": "npxg"})
            _xa = player.find("td", {"data-stat": "xa"})
            _npxg_per_shot = player.find("td", {"data-stat": "npxg_per_shot"})
            _xg_net = player.find("td", {"data-stat": "xg_net"})
            _npxg_net = player.find("td", {"data-stat": "npxg_net"})
            return PlayerStats(
                # common
                name=player.find("td", {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=player.find("td", {"data-stat": "squad"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                goals=int(_goals.text) if _goals else None,
                shots=int(_shots.text) if _shots else None,
                shots_on_target=int(_shots_on_target.text)
                if _shots_on_target
                else None,
                shots_on_target_pct=float(_shots_on_target_pct.text)
                if _shots_on_target_pct
                else None,
                shots_per90=float(_shots_per90.text) if _shots_per90 else None,
                shots_on_target_per90=float(_shots_on_target_per90.text)
                if _shots_on_target_per90
                else None,
                goals_per_shot=float(_goals_per_shot.text) if _goals_per_shot else None,
                goals_per_shot_on_target=float(_goals_per_shot_on_target.text)
                if _goals_per_shot_on_target
                else None,
                average_shot_distance=int(_average_shot_distance.text)
                if _average_shot_distance
                else None,
                shots_free_kicks=int(_shots_free_kicks.text)
                if _shots_free_kicks
                else None,
                pens_made=int(_pens_made.text) if _pens_made else None,
                pens_att=int(_pens_att.text) if _pens_att else None,
                xg=float(_xg.text) if _xg else None,
                npxg=float(_npxg.text) if _npxg else None,
                xa=float(_goals.text) if _xa else None,
                npxg_per_shot=float(_npxg_per_shot.text) if _npxg_per_shot else None,
                xg_net=float(_xg_net.text) if _xg_net else None,
                npxg_net=float(_npxg_net.text) if _npxg_net else None,
            )
        else:
            return None

    def __parse_player_passing_stat(
        self, player: Any, league_name: str
    ) -> Optional[PlayerStats]:
        if player.find("td", {"data-stat": "player"}) is not None:
            # all passes
            _passes_completed = player.find("td", {"data-stat": "passes_completed"})
            _passes = player.find("td", {"data-stat": "passes"})
            _passes_pct = player.find("td", {"data-stat": "passes_pct"})
            _passes_total_distance = player.find(
                "td", {"data-stat": "passes_total_distance"}
            )
            _passes_progressive_distance = player.find(
                "td", {"data-stat": "passes_progressive_distance"}
            )
            # short/medium/long passes
            _passes_completed_short = player.find(
                "td", {"data-stat": "passes_completed_short"}
            )
            _passes_short = player.find("td", {"data-stat": "passes_short"})
            _passes_pct_short = player.find("td", {"data-stat": "passes_pct_short"})
            _passes_completed_medium = player.find(
                "td", {"data-stat": "passes_completed_medium"}
            )
            _passes_medium = player.find("td", {"data-stat": "passes_medium"})
            _passes_pct_medium = player.find("td", {"data-stat": "passes_pct_medium"})
            _passes_completed_long = player.find(
                "td", {"data-stat": "passes_completed_long"}
            )
            _passes_long = player.find("td", {"data-stat": "passes_long"})
            _passes_pct_long = player.find("td", {"data-stat": "passes_pct_long"})
            # xa
            _assists = player.find("td", {"data-stat": "assists"})
            _xg_assist = player.find("td", {"data-stat": "xg_assist"})
            _pass_xa = player.find("td", {"data-stat": "pass_xa"})
            _xg_assist_net = player.find("td", {"data-stat": "xg_assist_net"})
            _assisted_shots = player.find("td", {"data-stat": "assisted_shots"})
            _passes_into_final_third = player.find(
                "td", {"data-stat": "passes_into_final_third"}
            )
            _passes_into_penalty_area = player.find(
                "td", {"data-stat": "passes_into_penalty_area"}
            )
            _crosses_into_penalty_area = player.find(
                "td", {"data-stat": "crosses_into_penalty_area"}
            )
            _progressive_passes = player.find("td", {"data-stat": "progressive_passes"})
            return PlayerStats(
                # common
                name=player.find("td", {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=player.find("td", {"data-stat": "squad"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                passes_completed=int(_passes_completed.text)
                if _passes_completed
                else None,
                passes=int(_passes.text) if _passes else None,
                passes_pct=float(_passes_pct.text) if _passes_pct else None,
                passes_total_distance=int(_passes_total_distance.text)
                if _passes_total_distance
                else None,
                passes_progressive_distance=int(_passes_progressive_distance.text)
                if _passes_progressive_distance
                else None,
                passes_short=int(_passes_short.text) if _passes_short else None,
                passes_completed_short=int(_passes_completed_short.text)
                if _passes_completed_short
                else None,
                passes_pct_short=float(_passes_pct_short.text)
                if _passes_pct_short
                else None,
                passes_medium=int(_passes_medium.text) if _passes_medium else None,
                passes_completed_medium=int(_passes_completed_medium.text)
                if _passes_completed_medium
                else None,
                passes_pct_medium=float(_passes_pct_medium.text)
                if _passes_pct_medium
                else None,
                passes_long=int(_passes_long.text) if _passes_long else None,
                passes_completed_long=int(_passes_completed_long.text)
                if _passes_completed_long
                else None,
                passes_pct_long=float(_passes_pct_long.text)
                if _passes_pct_long
                else None,
                assists=int(_assists.text) if _assists else None,
                xg_assist=float(_xg_assist.text) if _xg_assist else None,
                pass_xa=float(_pass_xa.text) if _pass_xa else None,
                xg_assist_net=float(_xg_assist_net.text) if _xg_assist_net else None,
                assisted_shots=int(_assisted_shots.text) if _assisted_shots else None,
                passes_into_final_third=int(_passes_into_final_third.text)
                if _passes_into_final_third
                else None,
                passes_into_penalty_area=int(_passes_into_penalty_area.text)
                if _passes_into_penalty_area
                else None,
                crosses_into_penalty_area=int(_crosses_into_penalty_area.text)
                if _crosses_into_penalty_area
                else None,
                progressive_passes=int(_progressive_passes.text)
                if _progressive_passes
                else None,
            )
        else:
            return None

    def __parse_player_pass_types_stat(
        self, player: Any, league_name: str
    ) -> Optional[PlayerStats]:
        if player.find("td", {"data-stat": "player"}) is not None:
            # all passes
            _passes_live = player.find("td", {"data-stat": "passes_live"})
            _passes_dead = player.find("td", {"data-stat": "passes_dead"})
            _passes_free_kicks = player.find("td", {"data-stat": "passes_free_kicks"})
            _through_balls = player.find("td", {"data-stat": "through_balls"})
            _passes_switches = player.find("td", {"data-stat": "passes_switches"})
            _crosses = player.find("td", {"data-stat": "crosses"})
            _throw_ins = player.find("td", {"data-stat": "throw_ins"})
            # corner kicks
            _corner_kicks = player.find("td", {"data-stat": "corner_kicks"})
            _corner_kicks_in = player.find("td", {"data-stat": "corner_kicks_in"})
            _corner_kicks_out = player.find("td", {"data-stat": "corner_kicks_out"})
            _corner_kicks_straight = player.find(
                "td", {"data-stat": "corner_kicks_straight"}
            )
            # passes
            _passes_completed = player.find("td", {"data-stat": "passes_completed"})
            _passes_offsides = player.find("td", {"data-stat": "passes_offsides"})
            _passes_blocked = player.find("td", {"data-stat": "passes_blocked"})
            return PlayerStats(
                # common
                name=player.find("td", {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=player.find("td", {"data-stat": "squad"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                passes_live=int(_passes_live.text) if _passes_live else None,
                passes_dead=int(_passes_dead.text) if _passes_dead else None,
                passes_free_kicks=int(_passes_free_kicks.text)
                if _passes_free_kicks
                else None,
                through_balls=int(_through_balls.text) if _through_balls else None,
                passes_switches=int(_passes_switches.text)
                if _passes_switches
                else None,
                crosses=int(_crosses.text) if _crosses else None,
                throw_ins=int(_throw_ins.text) if _throw_ins else None,
                corner_kicks=int(_corner_kicks.text) if _corner_kicks else None,
                corner_kicks_in=int(_corner_kicks_in.text)
                if _corner_kicks_in
                else None,
                corner_kicks_out=int(_corner_kicks_out.text)
                if _corner_kicks_out
                else None,
                corner_kicks_straight=int(_corner_kicks_straight.text)
                if _corner_kicks_straight
                else None,
                passes_completed=int(_passes_completed.text)
                if _passes_completed
                else None,
                passes_offsides=int(_passes_offsides.text)
                if _passes_offsides
                else None,
                passes_blocked=int(_passes_blocked.text) if _passes_blocked else None,
            )
        else:
            return None

    def __parse_player_possession_stat(
        self, player: Any, league_name: str
    ) -> Optional[PlayerStats]:
        if player.find("td", {"data-stat": "player"}) is not None:
            # touches
            _touches = player.find("td", {"data-stat": "touches"})
            _touches_def_pen_area = player.find(
                "td", {"data-stat": "touches_def_pen_area"}
            )
            _touches_def_3rd = player.find("td", {"data-stat": "touches_def_3rd"})
            _touches_mid_3rd = player.find("td", {"data-stat": "touches_mid_3rd"})
            _touches_att_3rd = player.find("td", {"data-stat": "touches_att_3rd"})
            _touches_att_pen_area = player.find(
                "td", {"data-stat": "touches_att_pen_area"}
            )
            _touches_live_ball = player.find("td", {"data-stat": "touches_live_ball"})
            # take_ons
            _take_ons = player.find("td", {"data-stat": "take_ons"})
            _take_ons_won = player.find("td", {"data-stat": "take_ons_won"})
            _take_ons_won_pct = player.find("td", {"data-stat": "take_ons_won_pct"})
            _take_ons_tackled = player.find("td", {"data-stat": "take_ons_tackled"})
            _take_ons_tackled_pct = player.find(
                "td", {"data-stat": "take_ons_tackled_pct"}
            )
            # carries
            _carries = player.find("td", {"data-stat": "carries"})
            _carries_distance = player.find("td", {"data-stat": "carries_distance"})
            _carries_progressive_distance = player.find(
                "td", {"data-stat": "carries_progressive_distance"}
            )
            _progressive_carries = player.find(
                "td", {"data-stat": "progressive_carries"}
            )
            _carries_into_final_third = player.find(
                "td", {"data-stat": "carries_into_final_third"}
            )
            _carries_into_penalty_area = player.find(
                "td", {"data-stat": "carries_into_penalty_area"}
            )
            _miscontrols = player.find("td", {"data-stat": "miscontrols"})
            _dispossessed = player.find("td", {"data-stat": "dispossessed"})
            _passes_received = player.find("td", {"data-stat": "passes_received"})
            _progressive_passes_received = player.find(
                "td", {"data-stat": "progressive_passes_received"}
            )
            return PlayerStats(
                # common
                name=player.find("td", {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=player.find("td", {"data-stat": "squad"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                touches=int(_touches.text) if _touches else None,
                touches_def_pen_area=int(_touches_def_pen_area.text)
                if _touches_def_pen_area
                else None,
                touches_def_3rd=int(_touches_def_3rd.text)
                if _touches_def_3rd
                else None,
                touches_mid_3rd=int(_touches_mid_3rd.text)
                if _touches_mid_3rd
                else None,
                touches_att_3rd=int(_touches_att_3rd.text)
                if _touches_att_3rd
                else None,
                touches_att_pen_area=int(_touches_att_pen_area.text)
                if _touches_att_pen_area
                else None,
                touches_live_ball=int(_touches_live_ball.text)
                if _touches_live_ball
                else None,
                # take_ons
                take_ons=int(_take_ons.text) if _take_ons else None,
                take_ons_won=int(_take_ons_won.text) if _take_ons_won else None,
                take_ons_won_pct=float(_take_ons_won_pct.text)
                if _take_ons_won_pct
                else None,
                take_ons_tackled=int(_take_ons_tackled.text)
                if _take_ons_tackled
                else None,
                take_ons_tackled_pct=float(_take_ons_tackled_pct.text)
                if _take_ons_tackled_pct
                else None,
                # carries
                carries=int(_carries.text) if _carries else None,
                carries_distance=int(_carries_distance.text)
                if _carries_distance
                else None,
                carries_progressive_distance=int(_carries_progressive_distance.text)
                if _carries_progressive_distance
                else None,
                progressive_carries=int(_progressive_carries.text)
                if _progressive_carries
                else None,
                carries_into_final_third=int(_carries_into_final_third.text)
                if _carries_into_final_third
                else None,
                carries_into_penalty_area=int(_carries_into_penalty_area.text)
                if _carries_into_penalty_area
                else None,
                miscontrols=int(_miscontrols.text) if _miscontrols else None,
                dispossessed=int(_dispossessed.text) if _dispossessed else None,
                passes_received=int(_passes_received.text)
                if _passes_received
                else None,
                progressive_passes_received=int(_progressive_passes_received.text)
                if _progressive_passes_received
                else None,
            )
        else:
            return None

    def __parse_player_shot_creation_stat(
        self, player: Any, league_name: str
    ) -> Optional[PlayerStats]:
        if player.find("td", {"data-stat": "player"}) is not None:
            _sca = player.find("td", {"data-stat": "sca"})
            _sca_per90 = player.find("td", {"data-stat": "sca_per90"})
            _sca_passes_live = player.find("td", {"data-stat": "sca_passes_live"})
            _sca_passes_dead = player.find("td", {"data-stat": "sca_passes_dead"})
            _sca_take_ons = player.find("td", {"data-stat": "sca_take_ons"})
            _sca_shots = player.find("td", {"data-stat": "sca_shots"})
            _sca_fouled = player.find("td", {"data-stat": "sca_fouled"})
            _sca_defense = player.find("td", {"data-stat": "sca_defense"})
            _gca = player.find("td", {"data-stat": "gca"})
            _gca_per90 = player.find("td", {"data-stat": "gca_per90"})
            _gca_passes_live = player.find("td", {"data-stat": "gca_passes_live"})
            _gca_passes_dead = player.find("td", {"data-stat": "gca_passes_dead"})
            _gca_take_ons = player.find("td", {"data-stat": "gca_take_ons"})
            _gca_shots = player.find("td", {"data-stat": "gca_shots"})
            _gca_fouled = player.find("td", {"data-stat": "gca_fouled"})
            _gca_defense = player.find("td", {"data-stat": "gca_defense"})
            return PlayerStats(
                # common
                name=player.find("td", {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=player.find("td", {"data-stat": "squad"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                sca=int(_sca.text) if _sca else None,
                sca_per90=float(_sca_per90.text) if _sca_per90 else None,
                sca_passes_live=int(_sca_passes_live.text)
                if _sca_passes_live
                else None,
                sca_passes_dead=int(_sca_passes_dead.text)
                if _sca_passes_dead
                else None,
                sca_take_ons=int(_sca_take_ons.text) if _sca_take_ons else None,
                sca_shots=int(_sca_shots.text) if _sca_shots else None,
                sca_fouled=int(_sca_fouled.text) if _sca_fouled else None,
                sca_defense=int(_sca_defense.text) if _sca_defense else None,
                gca=int(_gca.text) if _gca else None,
                gca_per90=float(_gca_per90.text) if _gca_per90 else None,
                gca_passes_live=int(_gca_passes_live.text)
                if _gca_passes_live
                else None,
                gca_passes_dead=int(_gca_passes_dead.text)
                if _gca_passes_dead
                else None,
                gca_take_ons=int(_gca_take_ons.text) if _gca_take_ons else None,
                gca_shots=int(_gca_shots.text) if _gca_shots else None,
                gca_fouled=int(_gca_fouled.text) if _gca_fouled else None,
                gca_defense=int(_gca_defense.text) if _gca_defense else None,
            )
        else:
            return None

    def __parse_player_playing_time_stat(
        self, player: Any, league_name: str
    ) -> Optional[PlayerStats]:
        if player.find("td", {"data-stat": "player"}) is not None:
            _games = player.find("td", {"data-stat": "games"})
            _minutes = player.find("td", {"data-stat": "minutes"})
            _minutes_per_game = player.find("td", {"data-stat": "minutes_per_game"})
            _minutes_pct = player.find("td", {"data-stat": "minutes_pct"})
            _minutes_90s = player.find("td", {"data-stat": "minutes_90s"})
            _games_starts = player.find("td", {"data-stat": "games_starts"})
            _minutes_per_start = player.find("td", {"data-stat": "minutes_per_start"})
            _games_complete = player.find("td", {"data-stat": "games_complete"})
            _games_subs = player.find("td", {"data-stat": "games_subs"})
            _minutes_per_sub = player.find("td", {"data-stat": "minutes_per_sub"})
            _unused_subs = player.find("td", {"data-stat": "unused_subs"})
            _points_per_game = player.find("td", {"data-stat": "points_per_game"})
            _on_goals_for = player.find("td", {"data-stat": "on_goals_for"})
            _on_goals_against = player.find("td", {"data-stat": "on_goals_against"})
            _plus_minus = player.find("td", {"data-stat": "plus_minus"})
            _plus_minus_per90 = player.find("td", {"data-stat": "plus_minus_per90"})
            _plus_minus_wowy = player.find("td", {"data-stat": "plus_minus_wowy"})
            _on_xg_for = player.find("td", {"data-stat": "on_xg_for"})
            _on_xg_against = player.find("td", {"data-stat": "on_xg_against"})
            _xg_plus_minus = player.find("td", {"data-stat": "xg_plus_minus"})
            _xg_plus_minus_per90 = player.find(
                "td", {"data-stat": "xg_plus_minus_per90"}
            )
            _xg_plus_minus_wowy = player.find("td", {"data-stat": "xg_plus_minus_wowy"})
            return PlayerStats(
                # common
                name=player.find("td", {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=player.find("td", {"data-stat": "squad"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                games=int(_games.text) if _games else None,
                minutes=int(_minutes.text) if _minutes else None,
                minutes_per_game=int(_minutes_per_game.text)
                if _minutes_per_game
                else None,
                minutes_pct=float(_minutes_pct.text) if _minutes_pct else None,
                minutes_90s=float(_minutes_90s.text) if _minutes_90s else None,
                games_starts=int(_games_starts.text) if _games_starts else None,
                minutes_per_start=int(_minutes_per_start.text)
                if _minutes_per_start
                else None,
                games_complete=int(_games_complete.text) if _games_complete else None,
                games_subs=int(_games_subs.text) if _games_subs else None,
                minutes_per_sub=int(_minutes_per_sub.text)
                if _minutes_per_sub
                else None,
                unused_subs=int(_unused_subs.text) if _unused_subs else None,
                points_per_game=float(_points_per_game.text)
                if _points_per_game
                else None,
                on_goals_for=int(_on_goals_for.text) if _on_goals_for else None,
                on_goals_against=int(_on_goals_against.text)
                if _on_goals_against
                else None,
                plus_minus=int(_plus_minus.text) if _plus_minus else None,
                plus_minus_per90=float(_plus_minus_per90.text)
                if _plus_minus_per90
                else None,
                plus_minus_wowy=float(_plus_minus_wowy.text)
                if _plus_minus_wowy
                else None,
                on_xg_for=float(_on_xg_for.text) if _on_xg_for else None,
                on_xg_against=float(_on_xg_against.text) if _on_xg_against else None,
                xg_plus_minus=float(_xg_plus_minus.text) if _xg_plus_minus else None,
                xg_plus_minus_per90=float(_xg_plus_minus_per90.text)
                if _xg_plus_minus_per90
                else None,
                xg_plus_minus_wowy=float(_xg_plus_minus_wowy.text)
                if _xg_plus_minus_wowy
                else None,
            )
        else:
            return None

    def __parse_league_stats(
        self, league_name: str, url: str, table_name: str, parse_func: Callable
    ) -> List[PlayerStats]:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", id_=table_name)
        players = table.find_all("tr")[2:]
        result = []
        for player in players:
            parsed_player = parse_func(player, league_name)
            if parsed_player is not None:
                result.append(parsed_player)
        return result

    def __update_players_stat(
        self,
        players: Dict[Tuple[str, str, str, str], PlayerStats],
        players_stat: List[PlayerStats],
    ) -> Dict[Tuple[str, str, str, str], PlayerStats]:
        for player in players_stat:
            if (
                player.name,
                player.team_name,
                player.position,
                player.league_name,
            ) in players:  # update none values
                old_player_stat = asdict(
                    players[
                        (
                            player.name,
                            player.team_name,
                            player.position,
                            player.league_name,
                        )
                    ]
                )
                # add new player stats
                old_player_stat.update(asdict(player))
                players[
                    (player.name, player.team_name, player.position, player.league_name)
                ] = PlayerStats(**old_player_stat)
            else:
                players[
                    (player.name, player.team_name, player.position, player.league_name)
                ] = player
        return players

    def get_stats_all_leagues(self) -> List[PlayerStats]:
        players: Dict[Tuple[str, str, str, str], PlayerStats] = {}
        try:
            # playing time stats
            for league_name, url in self.__playing_time_leagues.items():
                playing_time_players = self.__parse_league_stats(
                    league_name=league_name,
                    url=url,
                    table_name="stats_playing_time",
                    parse_func=self.__parse_player_playing_time_stat,
                )
                players = self.__update_players_stat(players, playing_time_players)
            # shooting stats
            for league_name, url in self.__playing_time_leagues.items():
                playing_time_players = self.__parse_league_stats(
                    league_name=league_name,
                    url=url,
                    table_name="stats_shooting",
                    parse_func=self.__parse_player_shooting_stat,
                )
                players = self.__update_players_stat(players, playing_time_players)
            # passing stats
            for league_name, url in self.__passing_leagues.items():
                passing_players = self.__parse_league_stats(
                    league_name=league_name,
                    url=url,
                    table_name="stats_passing",
                    parse_func=self.__parse_player_passing_stat,
                )
                players = self.__update_players_stat(players, passing_players)
            # pass types stats
            for league_name, url in self.__pass_types_leagues.items():
                pass_types_players = self.__parse_league_stats(
                    league_name=league_name,
                    url=url,
                    table_name="stats_passing_types",
                    parse_func=self.__parse_player_pass_types_stat,
                )
                players = self.__update_players_stat(players, pass_types_players)
            # possession stats
            for league_name, url in self.__possession_leagues.items():
                possession_players = self.__parse_league_stats(
                    league_name=league_name,
                    url=url,
                    table_name="stats_possession",
                    parse_func=self.__parse_player_possession_stat,
                )
                players = self.__update_players_stat(players, possession_players)
            # shot creation stats
            for league_name, url in self.__shot_creation_leagues.items():
                shot_creation_players = self.__parse_league_stats(
                    league_name=league_name,
                    url=url,
                    table_name="stats_gca",
                    parse_func=self.__parse_player_shot_creation_stat,
                )
                players = self.__update_players_stat(players, shot_creation_players)
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
        finally:
            return list(players.values())
