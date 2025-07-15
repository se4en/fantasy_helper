import logging
import os
import sys
import re
from datetime import date, datetime
from dataclasses import asdict
from typing import Any, Callable, Dict, Literal, Optional, List, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver import FirefoxOptions
from bs4 import BeautifulSoup

from fantasy_helper.utils.dataclasses import LeagueInfo, LeagueScheduleInfo, LeagueTableInfo, PlayerMatchStats, PlayerStats


def cast_to_float(text: str) -> Optional[float]:
    if not text:
        return None
    try:
        return float(text.strip())
    except ValueError:
        logging.warning(f"To float: text={text} len={len(text)}")
        return None


def cast_to_int(text: str) -> Optional[int]:
    if not text:
        return None
    elif "," in text:
        text = text.replace(",", "").strip()
    elif "(" in text and ")" in text:
        text = re.sub("\(.*?\)", "", text).strip()
    else:
        text = text.strip()
    try:
        return int(text)
    except ValueError:
        logging.warning(f"To int: text={text} len={len(text)}")
        return None


class FbrefParser:
    def __init__(self, leagues: List[LeagueInfo]):
        leagues = list(filter(lambda x: x.is_active, leagues))

        self._leagues_ids = {
            l.name: l.fbref_league_id for l in leagues if l.fbref_league_id is not None
        }
        self._table_leagues = {
            l.name: l.fbref_table_url
            for l in leagues
            if l.fbref_table_url is not None
        }
        self._schedule_leagues = {
            l.name: l.fbref_schedule_url
            for l in leagues
            if l.fbref_schedule_url is not None
        }
        self._playing_time_leagues = {
            l.name: l.fbref_playing_time_url
            for l in leagues
            if l.fbref_playing_time_url is not None
        }
        self._standart_leagues = {
            l.name: l.fbref_standart_url
            for l in leagues
            if l.fbref_standart_url is not None
        }
        self._shooting_leagues = {
            l.name: l.fbref_shooting_url
            for l in leagues
            if l.fbref_shooting_url is not None
        }
        self._passing_leagues = {
            l.name: l.fbref_passing_url
            for l in leagues
            if l.fbref_passing_url is not None
        }
        self._pass_types_leagues = {
            l.name: l.fbref_pass_types_url
            for l in leagues
            if l.fbref_pass_types_url is not None
        }
        self._possession_leagues = {
            l.name: l.fbref_possesion_url
            for l in leagues
            if l.fbref_possesion_url is not None
        }
        self._shot_creation_leagues = {
            l.name: l.fbref_shot_creation_url
            for l in leagues
            if l.fbref_shot_creation_url is not None
        }

    def get_playing_time_leagues(self) -> Dict[str, str]:
        return self._playing_time_leagues
    
    def get_standart_leagues(self) -> Dict[str, str]:
        return self._standart_leagues

    def get_shooting_leagues(self) -> Dict[str, str]:
        return self._shooting_leagues

    def get_passing_leagues(self) -> Dict[str, str]:
        return self._passing_leagues

    def get_pass_types_leagues(self) -> Dict[str, str]:
        return self._pass_types_leagues

    def get_possession_leagues(self) -> Dict[str, str]:
        return self._possession_leagues

    def get_shot_creation_leagues(self) -> Dict[str, str]:
        return self._shot_creation_leagues
    
    def get_schedule_leagues(self) -> Dict[str, str]:
        return self._schedule_leagues

    def _parse_player_summary_stat(
        self, 
        player: Any, 
        league_name: str, 
        team_name: Optional[str] = None,
        player_tag: Literal["td", "th"] = "td"
    ) -> Optional[PlayerStats]:
        if player.find(player_tag, {"data-stat": "player"}) is not None:
            return PlayerStats(
                # common
                name=player.find(player_tag, {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=team_name if team_name is not None 
                else player.find("td", {"data-stat": "team"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                minutes=cast_to_int(player.find("td", {"data-stat": "minutes"}).text)
                if player.find("td", {"data-stat": "minutes"}) is not None
                else None,
                # performance
                goals=cast_to_int(player.find("td", {"data-stat": "goals"}).text)
                if player.find("td", {"data-stat": "goals"}) is not None
                else None,
                assists=cast_to_int(player.find("td", {"data-stat": "assists"}).text)
                if player.find("td", {"data-stat": "assists"}) is not None
                else None,
                pens_made=cast_to_int(player.find("td", {"data-stat": "pens_made"}).text)
                if player.find("td", {"data-stat": "pens_made"}) is not None
                else None,
                pens_att=cast_to_int(player.find("td", {"data-stat": "pens_att"}).text)
                if player.find("td", {"data-stat": "pens_att"}) is not None
                else None,
                shots=cast_to_int(player.find("td", {"data-stat": "shots"}).text)
                if player.find("td", {"data-stat": "shots"}) is not None
                else None,
                shots_on_target=cast_to_int(
                    player.find("td", {"data-stat": "shots_on_target"}).text
                )
                if player.find("td", {"data-stat": "shots_on_target"}) is not None
                else None,
                yellow_cards=cast_to_int(
                    player.find("td", {"data-stat": "cards_yellow"}).text
                )
                if player.find("td", {"data-stat": "cards_yellow"}) is not None
                else None,
                red_cards=cast_to_int(player.find("td", {"data-stat": "cards_red"}).text)
                if player.find("td", {"data-stat": "cards_red"}) is not None
                else None,
                touches=cast_to_int(player.find("td", {"data-stat": "touches"}).text)
                if player.find("td", {"data-stat": "touches"}) is not None
                else None,
                # expected
                xg=cast_to_float(player.find("td", {"data-stat": "xg"}).text)
                if player.find("td", {"data-stat": "xg"}) is not None
                else None,
                xg_np=cast_to_float(player.find("td", {"data-stat": "npxg"}).text)
                if player.find("td", {"data-stat": "npxg"}) is not None
                else None,
                xg_assist=cast_to_float(
                    player.find("td", {"data-stat": "xg_assist"}).text
                )
                if player.find("td", {"data-stat": "xg_assist"}) is not None
                else None,
                # sca
                sca=cast_to_int(player.find("td", {"data-stat": "sca"}).text)
                if player.find("td", {"data-stat": "sca"}) is not None
                else None,
                gca=cast_to_int(player.find("td", {"data-stat": "gca"}).text)
                if player.find("td", {"data-stat": "gca"}) is not None
                else None,
                # passes
                passes_completed=cast_to_int(
                    player.find("td", {"data-stat": "passes_completed"}).text
                )
                if player.find("td", {"data-stat": "passes_completed"}) is not None
                else None,
                passes=cast_to_int(player.find("td", {"data-stat": "passes"}).text)
                if player.find("td", {"data-stat": "passes"}) is not None
                else None,
                passes_pct=cast_to_float(
                    player.find("td", {"data-stat": "passes_pct"}).text
                )
                if player.find("td", {"data-stat": "passes_pct"}) is not None
                else None,
                progressive_passes=cast_to_int(
                    player.find("td", {"data-stat": "progressive_passes"}).text
                )
                if player.find("td", {"data-stat": "progressive_passes"}) is not None
                else None,
                # carries
                carries=cast_to_int(player.find("td", {"data-stat": "carries"}).text)
                if player.find("td", {"data-stat": "carries"}) is not None
                else None,
                progressive_carries=cast_to_int(
                    player.find("td", {"data-stat": "progressive_carries"}).text
                )
                if player.find("td", {"data-stat": "progressive_carries"}) is not None
                else None,
                # take-ons
                take_ons=cast_to_int(
                    player.find("td", {"data-stat": "take_ons"}).text
                )
                if player.find("td", {"data-stat": "take_ons"}) is not None
                else None,
                take_ons_won=cast_to_int(
                    player.find("td", {"data-stat": "take_ons_won"}).text
                )
                if player.find("td", {"data-stat": "take_ons_won"}) is not None
                else None
            )
        else:
            return None

    def _parse_player_shooting_stat(
        self, 
        player: Any, 
        league_name: str, 
        team_name: Optional[str] = None,
        player_tag: Literal["td", "th"] = "td"
    ) -> Optional[PlayerStats]:
        if player.find(player_tag, {"data-stat": "player"}) is not None:
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
                name=player.find(player_tag, {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=team_name if team_name is not None 
                else player.find("td", {"data-stat": "team"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                goals=cast_to_int(_goals.text) if _goals else None,
                shots=cast_to_int(_shots.text) if _shots else None,
                shots_on_target=cast_to_int(_shots_on_target.text)
                if _shots_on_target
                else None,
                shots_on_target_pct=cast_to_float(_shots_on_target_pct.text)
                if _shots_on_target_pct
                else None,
                shots_per90=cast_to_float(_shots_per90.text) if _shots_per90 else None,
                shots_on_target_per90=cast_to_float(_shots_on_target_per90.text)
                if _shots_on_target_per90
                else None,
                goals_per_shot=cast_to_float(_goals_per_shot.text)
                if _goals_per_shot
                else None,
                goals_per_shot_on_target=cast_to_float(_goals_per_shot_on_target.text)
                if _goals_per_shot_on_target
                else None,
                average_shot_distance=cast_to_float(_average_shot_distance.text)
                if _average_shot_distance
                else None,
                shots_free_kicks=cast_to_int(_shots_free_kicks.text)
                if _shots_free_kicks
                else None,
                pens_made=cast_to_int(_pens_made.text) if _pens_made else None,
                pens_att=cast_to_int(_pens_att.text) if _pens_att else None,
                xg=cast_to_float(_xg.text) if _xg else None,
                npxg=cast_to_float(_npxg.text) if _npxg else None,
                xa=cast_to_float(_goals.text) if _xa else None,
                npxg_per_shot=cast_to_float(_npxg_per_shot.text)
                if _npxg_per_shot
                else None,
                xg_net=cast_to_float(_xg_net.text) if _xg_net else None,
                npxg_net=cast_to_float(_npxg_net.text) if _npxg_net else None,
            )
        else:
            return None

    def _parse_player_passing_stat(
        self, 
        player: Any, 
        league_name: str, 
        team_name: Optional[str] = None,
        player_tag: Literal["td", "th"] = "td"
    ) -> Optional[PlayerStats]:
        if player.find(player_tag, {"data-stat": "player"}) is not None:
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
                name=player.find(player_tag, {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=team_name if team_name is not None 
                else player.find("td", {"data-stat": "team"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                passes_completed=cast_to_int(_passes_completed.text)
                if _passes_completed
                else None,
                passes=cast_to_int(_passes.text) if _passes else None,
                passes_pct=cast_to_float(_passes_pct.text) if _passes_pct else None,
                passes_total_distance=cast_to_int(_passes_total_distance.text)
                if _passes_total_distance
                else None,
                passes_progressive_distance=cast_to_int(
                    _passes_progressive_distance.text
                )
                if _passes_progressive_distance
                else None,
                passes_short=cast_to_int(_passes_short.text) if _passes_short else None,
                passes_completed_short=cast_to_int(_passes_completed_short.text)
                if _passes_completed_short
                else None,
                passes_pct_short=cast_to_float(_passes_pct_short.text)
                if _passes_pct_short
                else None,
                passes_medium=cast_to_int(_passes_medium.text)
                if _passes_medium
                else None,
                passes_completed_medium=cast_to_int(_passes_completed_medium.text)
                if _passes_completed_medium
                else None,
                passes_pct_medium=cast_to_float(_passes_pct_medium.text)
                if _passes_pct_medium
                else None,
                passes_long=cast_to_int(_passes_long.text) if _passes_long else None,
                passes_completed_long=cast_to_int(_passes_completed_long.text)
                if _passes_completed_long
                else None,
                passes_pct_long=cast_to_float(_passes_pct_long.text)
                if _passes_pct_long
                else None,
                assists=cast_to_int(_assists.text) if _assists else None,
                xg_assist=cast_to_float(_xg_assist.text) if _xg_assist else None,
                pass_xa=cast_to_float(_pass_xa.text) if _pass_xa else None,
                xg_assist_net=cast_to_float(_xg_assist_net.text)
                if _xg_assist_net
                else None,
                assisted_shots=cast_to_int(_assisted_shots.text)
                if _assisted_shots
                else None,
                passes_into_final_third=cast_to_int(_passes_into_final_third.text)
                if _passes_into_final_third
                else None,
                passes_into_penalty_area=cast_to_int(_passes_into_penalty_area.text)
                if _passes_into_penalty_area
                else None,
                crosses_into_penalty_area=cast_to_int(_crosses_into_penalty_area.text)
                if _crosses_into_penalty_area
                else None,
                progressive_passes=cast_to_int(_progressive_passes.text)
                if _progressive_passes
                else None,
            )
        else:
            return None

    def _parse_player_pass_types_stat(
        self, 
        player: Any, 
        league_name: str, 
        team_name: Optional[str] = None,
        player_tag: Literal["td", "th"] = "td"
    ) -> Optional[PlayerStats]:
        if player.find(player_tag, {"data-stat": "player"}) is not None:
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
                name=player.find(player_tag, {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=team_name if team_name is not None 
                else player.find("td", {"data-stat": "team"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                passes_live=cast_to_int(_passes_live.text) if _passes_live else None,
                passes_dead=cast_to_int(_passes_dead.text) if _passes_dead else None,
                passes_free_kicks=cast_to_int(_passes_free_kicks.text)
                if _passes_free_kicks
                else None,
                through_balls=cast_to_int(_through_balls.text)
                if _through_balls
                else None,
                passes_switches=cast_to_int(_passes_switches.text)
                if _passes_switches
                else None,
                crosses=cast_to_int(_crosses.text) if _crosses else None,
                throw_ins=cast_to_int(_throw_ins.text) if _throw_ins else None,
                corner_kicks=cast_to_int(_corner_kicks.text) if _corner_kicks else None,
                corner_kicks_in=cast_to_int(_corner_kicks_in.text)
                if _corner_kicks_in
                else None,
                corner_kicks_out=cast_to_int(_corner_kicks_out.text)
                if _corner_kicks_out
                else None,
                corner_kicks_straight=cast_to_int(_corner_kicks_straight.text)
                if _corner_kicks_straight
                else None,
                passes_completed=cast_to_int(_passes_completed.text)
                if _passes_completed
                else None,
                passes_offsides=cast_to_int(_passes_offsides.text)
                if _passes_offsides
                else None,
                passes_blocked=cast_to_int(_passes_blocked.text)
                if _passes_blocked
                else None,
            )
        else:
            return None

    def _parse_player_possession_stat(
        self, 
        player: Any, 
        league_name: str, 
        team_name: Optional[str] = None,
        player_tag: Literal["td", "th"] = "td"
    ) -> Optional[PlayerStats]:
        if player.find(player_tag, {"data-stat": "player"}) is not None:
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
            # receiving
            _passes_received = player.find("td", {"data-stat": "passes_received"})
            _progressive_passes_received = player.find(
                "td", {"data-stat": "progressive_passes_received"}
            )
            return PlayerStats(
                # common
                name=player.find(player_tag, {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=team_name if team_name is not None 
                else player.find("td", {"data-stat": "team"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                touches=cast_to_int(_touches.text) if _touches else None,
                touches_def_pen_area=cast_to_int(_touches_def_pen_area.text)
                if _touches_def_pen_area
                else None,
                touches_def_3rd=cast_to_int(_touches_def_3rd.text)
                if _touches_def_3rd
                else None,
                touches_mid_3rd=cast_to_int(_touches_mid_3rd.text)
                if _touches_mid_3rd
                else None,
                touches_att_3rd=cast_to_int(_touches_att_3rd.text)
                if _touches_att_3rd
                else None,
                touches_att_pen_area=cast_to_int(_touches_att_pen_area.text)
                if _touches_att_pen_area
                else None,
                touches_live_ball=cast_to_int(_touches_live_ball.text)
                if _touches_live_ball
                else None,
                # take_ons
                take_ons=cast_to_int(_take_ons.text) if _take_ons else None,
                take_ons_won=cast_to_int(_take_ons_won.text) if _take_ons_won else None,
                take_ons_won_pct=cast_to_float(_take_ons_won_pct.text)
                if _take_ons_won_pct
                else None,
                take_ons_tackled=cast_to_int(_take_ons_tackled.text)
                if _take_ons_tackled
                else None,
                take_ons_tackled_pct=cast_to_float(_take_ons_tackled_pct.text)
                if _take_ons_tackled_pct
                else None,
                # carries
                carries=cast_to_int(_carries.text) if _carries else None,
                carries_distance=cast_to_int(_carries_distance.text)
                if _carries_distance
                else None,
                carries_progressive_distance=cast_to_int(
                    _carries_progressive_distance.text
                )
                if _carries_progressive_distance
                else None,
                progressive_carries=cast_to_int(_progressive_carries.text)
                if _progressive_carries
                else None,
                carries_into_final_third=cast_to_int(_carries_into_final_third.text)
                if _carries_into_final_third
                else None,
                carries_into_penalty_area=cast_to_int(_carries_into_penalty_area.text)
                if _carries_into_penalty_area
                else None,
                miscontrols=cast_to_int(_miscontrols.text) if _miscontrols else None,
                dispossessed=cast_to_int(_dispossessed.text) if _dispossessed else None,
                passes_received=cast_to_int(_passes_received.text)
                if _passes_received
                else None,
                progressive_passes_received=cast_to_int(
                    _progressive_passes_received.text
                )
                if _progressive_passes_received
                else None,
            )
        else:
            return None

    def _parse_player_shot_creation_stat(
        self, 
        player: Any, 
        league_name: str, 
        team_name: Optional[str] = None,
        player_tag: Literal["td", "th"] = "td"
    ) -> Optional[PlayerStats]:
        if player.find(player_tag, {"data-stat": "player"}) is not None:
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
                name=player.find(player_tag, {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=team_name if team_name is not None 
                else player.find("td", {"data-stat": "team"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                sca=cast_to_int(_sca.text) if _sca else None,
                sca_per90=cast_to_float(_sca_per90.text) if _sca_per90 else None,
                sca_passes_live=cast_to_int(_sca_passes_live.text)
                if _sca_passes_live
                else None,
                sca_passes_dead=cast_to_int(_sca_passes_dead.text)
                if _sca_passes_dead
                else None,
                sca_take_ons=cast_to_int(_sca_take_ons.text) if _sca_take_ons else None,
                sca_shots=cast_to_int(_sca_shots.text) if _sca_shots else None,
                sca_fouled=cast_to_int(_sca_fouled.text) if _sca_fouled else None,
                sca_defense=cast_to_int(_sca_defense.text) if _sca_defense else None,
                gca=cast_to_int(_gca.text) if _gca else None,
                gca_per90=cast_to_float(_gca_per90.text) if _gca_per90 else None,
                gca_passes_live=cast_to_int(_gca_passes_live.text)
                if _gca_passes_live
                else None,
                gca_passes_dead=cast_to_int(_gca_passes_dead.text)
                if _gca_passes_dead
                else None,
                gca_take_ons=cast_to_int(_gca_take_ons.text) if _gca_take_ons else None,
                gca_shots=cast_to_int(_gca_shots.text) if _gca_shots else None,
                gca_fouled=cast_to_int(_gca_fouled.text) if _gca_fouled else None,
                gca_defense=cast_to_int(_gca_defense.text) if _gca_defense else None,
            )
        else:
            return None

    def _parse_player_playing_time_stat(
        self, 
        player: Any, 
        league_name: str, 
        team_name: Optional[str] = None,
        player_tag: Literal["td", "th"] = "td"
    ) -> Optional[PlayerStats]:
        if player.find(player_tag, {"data-stat": "player"}) is not None:
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
            _points_per_game = player.find(
                "td", {"data-stat": "pocast_to_ints_per_game"}
            )
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
                name=player.find(player_tag, {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=team_name if team_name is not None 
                else player.find("td", {"data-stat": "team"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                games=cast_to_int(_games.text) if _games else None,
                minutes=cast_to_int(_minutes.text) if _minutes else None,
                minutes_per_game=cast_to_int(_minutes_per_game.text)
                if _minutes_per_game
                else None,
                minutes_pct=cast_to_float(_minutes_pct.text) if _minutes_pct else None,
                minutes_90s=cast_to_float(_minutes_90s.text) if _minutes_90s else None,
                games_starts=cast_to_int(_games_starts.text) if _games_starts else None,
                minutes_per_start=cast_to_int(_minutes_per_start.text)
                if _minutes_per_start
                else None,
                games_complete=cast_to_int(_games_complete.text)
                if _games_complete
                else None,
                games_subs=cast_to_int(_games_subs.text) if _games_subs else None,
                minutes_per_sub=cast_to_int(_minutes_per_sub.text)
                if _minutes_per_sub
                else None,
                unused_subs=cast_to_int(_unused_subs.text) if _unused_subs else None,
                points_per_game=cast_to_float(_points_per_game.text)
                if _points_per_game
                else None,
                on_goals_for=cast_to_int(_on_goals_for.text) if _on_goals_for else None,
                on_goals_against=cast_to_int(_on_goals_against.text)
                if _on_goals_against
                else None,
                plus_minus=cast_to_int(_plus_minus.text) if _plus_minus else None,
                plus_minus_per90=cast_to_float(_plus_minus_per90.text)
                if _plus_minus_per90
                else None,
                plus_minus_wowy=cast_to_float(_plus_minus_wowy.text)
                if _plus_minus_wowy
                else None,
                on_xg_for=cast_to_float(_on_xg_for.text) if _on_xg_for else None,
                on_xg_against=cast_to_float(_on_xg_against.text)
                if _on_xg_against
                else None,
                xg_plus_minus=cast_to_float(_xg_plus_minus.text)
                if _xg_plus_minus
                else None,
                xg_plus_minus_per90=cast_to_float(_xg_plus_minus_per90.text)
                if _xg_plus_minus_per90
                else None,
                xg_plus_minus_wowy=cast_to_float(_xg_plus_minus_wowy.text)
                if _xg_plus_minus_wowy
                else None,
            )
        else:
            return None
        
    def _parse_player_standart_stat(
        self, 
        player: Any, 
        league_name: str, 
        team_name: Optional[str] = None,
        player_tag: Literal["td", "th"] = "td"
    ) -> Optional[PlayerStats]:
        if player.find(player_tag, {"data-stat": "player"}) is not None:
            _games = player.find("td", {"data-stat": "games"})
            _games_starts = player.find("td", {"data-stat": "games_starts"})
            _minutes = player.find("td", {"data-stat": "minutes"})
            _goals = player.find("td", {"data-stat": "goals"})
            _assists = player.find("td", {"data-stat": "assists"})
            _yellow_cards = player.find("td", {"data-stat": "cards_yellow"})
            _red_cards = player.find("td", {"data-stat": "cards_red"})
            return PlayerStats(
                # common
                name=player.find(player_tag, {"data-stat": "player"}).text,
                league_name=league_name,
                team_name=team_name if team_name is not None 
                else player.find("td", {"data-stat": "team"}).text,
                position=player.find("td", {"data-stat": "position"}).text,
                # stats
                games=cast_to_int(_games.text) if _games else None,
                games_starts=cast_to_int(_games_starts.text) if _games_starts else None,
                minutes=cast_to_int(_minutes.text) if _minutes else None,
                goals=cast_to_int(_goals.text) if _goals else None,
                assists=cast_to_int(_assists.text) if _assists else None,
                yellow_cards=cast_to_int(_yellow_cards.text) if _yellow_cards else None,
                red_cards=cast_to_int(_red_cards.text) if _red_cards else None,
            )
        else:
            return None

    def _parse_league_stats(
        self, league_name: str, url: str, table_name: str, parse_func: Callable
    ) -> List[PlayerStats]:
        driver = None
        try:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
            opts.add_argument("--disable-blink-features=AutomationControlled")

            driver = webdriver.Firefox(
                executable_path=os.environ["GECKODRIVER_PATH"], options=opts
            )
            driver.get(url)
            players_table = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, table_name))
            )
            parsed_players_table = BeautifulSoup(
                players_table.get_attribute("outerHTML"), "html.parser"
            )
            players = parsed_players_table.find_all("tr")[2:]
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            logging.warning(
                f"league_name={league_name} url={url} table_name={table_name}"
            )
            return []
        else:
            result = []
            for player in players:
                parsed_player = parse_func(player, league_name)
                if parsed_player is not None:
                    result.append(parsed_player)
            return result
        finally:
            if driver is not None:
                driver.quit()

    def _parse_team_table_row(
        self, table_row: Any, league_name: str
    ) -> Optional[LeagueTableInfo]:
        if table_row.find("td", {"data-stat": "team"}) is not None:
            _team_name = table_row.find("td", {"data-stat": "team"})
            _rank = table_row.find("th", {"data-stat": "rank"})
            _wins = table_row.find("td", {"data-stat": "wins"})
            _draws = table_row.find("td", {"data-stat": "ties"})
            _losses = table_row.find("td", {"data-stat": "losses"})
            _points = table_row.find("td", {"data-stat": "points"})
            _goals_for = table_row.find("td", {"data-stat": "goals_for"})
            _goals_against = table_row.find("td", {"data-stat": "goals_against"})
            _xg_for = table_row.find("td", {"data-stat": "xg_for"})
            _xg_against = table_row.find("td", {"data-stat": "xg_against"})
            return LeagueTableInfo(
                league_name=league_name,
                team_name=_team_name.text.strip(),
                rank=cast_to_int(_rank.text) if _rank else None,
                wins=cast_to_int(_wins.text) if _wins else None,
                draws=cast_to_int(_draws.text) if _draws else None,
                losses=cast_to_int(_losses.text) if _losses else None,
                points=cast_to_int(_points.text) if _points else None,
                goals_for=cast_to_int(_goals_for.text) if _goals_for else None,
                goals_against=cast_to_int(_goals_against.text)
                if _goals_against
                else None,
                xg_for=cast_to_float(_xg_for.text) if _xg_for else None,
                xg_against=cast_to_float(_xg_against.text) if _xg_against else None,
            )
        else:
            return None

    def get_league_table(self, league_name: str, league_year: str = "2024") -> List[LeagueTableInfo]:
        if league_name not in self._table_leagues:
            return []
        if league_name not in self._leagues_ids:
            return []
        league_id = self._leagues_ids[league_name]
        driver = None

        try:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
            opts.add_argument("--disable-blink-features=AutomationControlled")

            driver = webdriver.Firefox(
                executable_path=os.environ["GECKODRIVER_PATH"], options=opts
            )
            driver.get(self._table_leagues[league_name])
            league_table = WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((
                    By.ID, 
                    f"results{cast_to_int(league_year)}-{cast_to_int(league_year)+1}{league_id}1_overall"
                ))
            )
            parsed_league_table = BeautifulSoup(
                league_table.get_attribute("outerHTML"), "html.parser"
            )
            table_rows = parsed_league_table.find_all("tr")[1:]
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            logging.warning(f"league_name={league_name}")
            return []
        else:
            result = []
            for table_row in table_rows:
                parsed_table_row = self._parse_team_table_row(table_row, league_name)
                if parsed_table_row is not None:
                    result.append(parsed_table_row)
            return result
        finally:
            if driver is not None:
                driver.quit()

    @staticmethod
    def _parse_fbref_date(date_str: str) -> Optional[date]:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return None

    def _parse_schedule_row(
        self, table_row: Any, league_name: str, cup: bool = False
    ) -> Optional[LeagueScheduleInfo]:
        _home_team = table_row.find("td", {"data-stat": "home_team"})
        if _home_team is not None and _home_team.text.strip() != "":
            _gameweek = table_row.find("td", {"data-stat": "gameweek"})
            _away_team = table_row.find("td", {"data-stat": "away_team"})
            _date = table_row.find("td", {"data-stat": "date"})
            _score = table_row.find("td", {"data-stat": "score"})
            _home_xg = table_row.find("td", {"data-stat": "home_xg"})
            _away_xg = table_row.find("td", {"data-stat": "away_xg"})

            if _score.text:
                goals = _score.text.split("–")
                _home_goals = cast_to_int(goals[0])
                _away_goals = cast_to_int(goals[1])
                _match_url = "https://fbref.com" + _score.find("a").get("href")
            else:
                _home_goals, _away_goals = None, None
                _match_url = None

            if cup:
                home_team = " ".join(_home_team.text.strip().split(" ")[:-1])
                away_team = " ".join(_away_team.text.strip().split(" ")[1:])
            else:
                home_team = _home_team.text.strip()
                away_team = _away_team.text.strip()

            return LeagueScheduleInfo(
                league_name=league_name,
                gameweek=cast_to_int(_gameweek.text) if _gameweek is not None else None,
                home_team=home_team,
                away_team=away_team,
                date=self._parse_fbref_date(_date.text.strip()) if _date is not None else None,
                home_goals=_home_goals,
                away_goals=_away_goals,
                home_xg=cast_to_float(_home_xg.text) if _home_xg is not None else None,
                away_xg=cast_to_float(_away_xg.text) if _away_xg is not None else None,
                match_url=_match_url
            )
        else:
            return None

    def get_league_schedule(self, league_name: str, cup: bool = False, league_year: str = "2024") -> List[LeagueScheduleInfo]:
        if league_name not in self._schedule_leagues:
            return []
        if league_name not in self._leagues_ids:
            return []
        league_id = self._leagues_ids[league_name]
        driver = None

        try:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
            opts.add_argument("--disable-blink-features=AutomationControlled")

            driver = webdriver.Firefox(
                executable_path=os.environ["GECKODRIVER_PATH"], options=opts
            )
            driver.get(self._schedule_leagues[league_name])
            if cup:
                league_schedule = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.ID, f"div_sched_all"))
                )
            else:
                league_schedule = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((
                        By.ID, 
                        f"sched_{cast_to_int(league_year)}-{cast_to_int(league_year)+1}_{league_id}_1"
                    ))
                )
                # todo: add sched_2025-2026_<>
            parsed_league_schedule = BeautifulSoup(
                league_schedule.get_attribute("outerHTML"), "html.parser"
            )
            schedule_rows = parsed_league_schedule.find_all("tr")[1:]
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            logging.warning(f"league_name={league_name}")
            return []
        else:
            result = []
            for table_row in schedule_rows:
                parsed_table_row = self._parse_schedule_row(table_row, league_name, cup)
                if parsed_table_row is not None:
                    result.append(parsed_table_row)
            return result
        finally:
            if driver is not None:
                driver.quit()

    def _update_player_stat(
        self, old_player_stat: PlayerStats, new_player_stat: PlayerStats
    ) -> PlayerStats:
        old_dict_stat = asdict(old_player_stat)
        new_dict_stat = asdict(new_player_stat)

        for key in old_dict_stat:
            if key in new_dict_stat and new_dict_stat[key] is not None:
                old_dict_stat[key] = new_dict_stat[key]

        return PlayerStats(**old_dict_stat)

    def _update_player_match_stat(
        self, old_player_stat: PlayerMatchStats, new_player_stat: PlayerMatchStats
    ) -> PlayerStats:
        old_dict_stat = asdict(old_player_stat)
        new_dict_stat = asdict(new_player_stat)

        for key in old_dict_stat:
            if key in new_dict_stat and new_dict_stat[key] is not None:
                old_dict_stat[key] = new_dict_stat[key]

        return PlayerMatchStats(**old_dict_stat)

    def _update_players_stat(
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
                old_player_stat = players[
                    (
                        player.name,
                        player.team_name,
                        player.position,
                        player.league_name,
                    )
                ]
                # add new player stats
                new_player_stat = self._update_player_stat(old_player_stat, player)
                players[
                    (player.name, player.team_name, player.position, player.league_name)
                ] = PlayerStats(**asdict(new_player_stat))
            else:
                players[
                    (player.name, player.team_name, player.position, player.league_name)
                ] = player
        return players

    def _update_players_match_stat(
        self,
        players: Dict[str, PlayerMatchStats],
        players_stat: List[PlayerMatchStats]
    ) -> Dict[str, PlayerMatchStats]:
        for player in players_stat:
            if player.player_id in players:
                old_player_stat = players[player.player_id]
                new_player_stat = self._update_player_match_stat(old_player_stat, player)
                players[player.player_id] = PlayerMatchStats(**asdict(new_player_stat))
            else:
                players[player.player_id] = player

        return players

    def _parse_player_match_summary_stat(
        self,
        player: Any,
        league_name: str,
        team_name: str
    ) -> Optional[PlayerMatchStats]:
        if player.find("th", {"data-stat": "player"}) is not None:
            # common
            _player = player.find("th", {"data-stat": "player"})
            if _player is None or _player.get("data-append-csv") is None:
                return None
            _shirt_number = player.find("td", {"data-stat": "shirtnumber"})
            _nationality = player.find("td", {"data-stat": "nationality"})
            _position = player.find("td", {"data-stat": "position"})
            _minutes = player.find("td", {"data-stat": "minutes"})
            # performance
            _goals = player.find("td", {"data-stat": "goals"})
            _assists = player.find("td", {"data-stat": "assists"})
            _pens_made = player.find("td", {"data-stat": "pens_made"})
            _pens_att = player.find("td", {"data-stat": "pens_att"})
            _shots = player.find("td", {"data-stat": "shots"})
            _shots_on_target = player.find("td", {"data-stat": "shots_on_target"})
            _yellow_cards = player.find("td", {"data-stat": "cards_yellow"})
            _red_cards = player.find("td", {"data-stat": "cards_red"})
            _touches = player.find("td", {"data-stat": "touches"})
            _tackles = player.find("td", {"data-stat": "tackles"})
            _interceptions = player.find("td", {"data-stat": "interceptions"})
            _blocks = player.find("td", {"data-stat": "blocks"})
            # expected
            _xg = player.find("td", {"data-stat": "xg"})
            _npxg = player.find("td", {"data-stat": "npxg"})
            _xg_assist = player.find("td", {"data-stat": "xg_assist"})
            _sca = player.find("td", {"data-stat": "sca"})
            _gca = player.find("td", {"data-stat": "gca"})
            # passes
            _passes_completed = player.find("td", {"data-stat": "passes_completed"})
            _passes = player.find("td", {"data-stat": "passes"})
            _passes_pct = player.find("td", {"data-stat": "passes_pct"})
            _progressive_passes = player.find("td", {"data-stat": "progressive_passes"})
            # carries
            _carries = player.find("td", {"data-stat": "carries"})
            _progressive_carries = player.find("td", {"data-stat": "progressive_carries"})
            # take-ons
            _take_ons = player.find("td", {"data-stat": "take_ons"})
            _take_ons_won = player.find("td", {"data-stat": "take_ons_won"})

            return PlayerMatchStats(
                # common
                name=_player.text.strip(),
                player_id=_player["data-append-csv"],
                shirt_number=cast_to_int(_shirt_number.text) if _shirt_number is not None else None,
                nationality=_nationality.text.split(" ")[-1] if _nationality is not None else None,
                position=_position.text if _position is not None else None,
                minutes=cast_to_int(_minutes.text) if _minutes is not None else None,
                player_url= "https://fbref.com" + _player.find("a").get("href")
                if _player.find("a") is not None and _player.find("a").get("href") is not None
                else None,
                league_name=league_name,
                team_name=team_name,
                # performance
                goals=cast_to_int(_goals.text) if _goals is not None else None,
                assists=cast_to_int(_assists.text) if _assists is not None else None,
                pens_made=cast_to_int(_pens_made.text) if _pens_made is not None else None,
                pens_att=cast_to_int(_pens_att.text) if _pens_att is not None else None,
                shots=cast_to_int(_shots.text) if _shots is not None else None,
                shots_on_target=cast_to_int(_shots_on_target.text)
                if _shots_on_target is not None
                else None,
                yellow_cards=cast_to_int(_yellow_cards.text)
                if _yellow_cards is not None
                else None,
                red_cards=cast_to_int(_red_cards.text) if _red_cards is not None else None,
                touches=cast_to_int(_touches.text) if _touches is not None else None,
                tackles=cast_to_int(_tackles.text) if _tackles is not None else None,
                interceptions=cast_to_int(_interceptions.text)
                if _interceptions is not None
                else None,
                blocks=cast_to_int(_blocks.text) if _blocks is not None else None,
                # expected
                xg=cast_to_float(_xg.text) if _xg is not None else None,
                xg_np=cast_to_float(_npxg.text) if _npxg is not None else None,
                xg_assist=cast_to_float(_xg_assist.text)
                if _xg_assist is not None
                else None,
                sca=cast_to_float(_sca.text) if _sca is not None else None,
                gca=cast_to_float(_gca.text) if _gca is not None else None,
                # passes
                passes_completed=cast_to_int(_passes_completed.text)
                if _passes_completed is not None
                else None,
                passes=cast_to_int(_passes.text) if _passes is not None else None,
                passes_pct=cast_to_float(_passes_pct.text)
                if _passes_pct is not None
                else None,
                progressive_passes=cast_to_int(_progressive_passes.text)
                if _progressive_passes is not None
                else None,
                # carries
                carries=cast_to_int(_carries.text) if _carries is not None else None,
                progressive_carries=cast_to_int(_progressive_carries.text)
                if _progressive_carries is not None
                else None,
                # take-ons
                take_ons=cast_to_int(_take_ons.text) if _take_ons is not None else None,
                take_ons_won=cast_to_int(_take_ons_won.text)
                if _take_ons_won is not None
                else None
            )
        else:
            return None

    def _parse_player_match_passing_stat(
        self,
        player: Any,
        league_name: str,
        team_name: str
    ) -> Optional[PlayerMatchStats]:
        if player.find("th", {"data-stat": "player"}) is not None:
            # common
            _player = player.find("th", {"data-stat": "player"})
            if _player is None or _player.get("data-append-csv") is None:
                return None
            _shirt_number = player.find("td", {"data-stat": "shirtnumber"})
            _nationality = player.find("td", {"data-stat": "nationality"})
            _position = player.find("td", {"data-stat": "position"})
            _minutes = player.find("td", {"data-stat": "minutes"})
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
            # assists
            _assists = player.find("td", {"data-stat": "assists"})
            _xg_assist = player.find("td", {"data-stat": "xg_assist"})
            _pass_xa = player.find("td", {"data-stat": "pass_xa"})
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
            return PlayerMatchStats(
                # common
                name=_player.text.strip(),
                player_id=_player["data-append-csv"],
                shirt_number=cast_to_int(_shirt_number.text),
                nationality=_nationality.text.split(" ")[-1],
                position=_position.text,
                minutes=cast_to_int(_minutes.text),
                player_url= "https://fbref.com" + _player.find("a").get("href")
                if _player.find("a") is not None and _player.find("a").get("href") is not None
                else None,
                league_name=league_name,
                team_name=team_name,
                # stats
                passes_completed=cast_to_int(_passes_completed.text)
                if _passes_completed
                else None,
                passes=cast_to_int(_passes.text) if _passes else None,
                passes_pct=cast_to_float(_passes_pct.text) if _passes_pct else None,
                passes_total_distance=cast_to_int(_passes_total_distance.text)
                if _passes_total_distance
                else None,
                passes_progressive_distance=cast_to_int(
                    _passes_progressive_distance.text
                )
                if _passes_progressive_distance
                else None,
                passes_short=cast_to_int(_passes_short.text) if _passes_short else None,
                passes_completed_short=cast_to_int(_passes_completed_short.text)
                if _passes_completed_short
                else None,
                passes_pct_short=cast_to_float(_passes_pct_short.text)
                if _passes_pct_short
                else None,
                passes_medium=cast_to_int(_passes_medium.text)
                if _passes_medium
                else None,
                passes_completed_medium=cast_to_int(_passes_completed_medium.text)
                if _passes_completed_medium
                else None,
                passes_pct_medium=cast_to_float(_passes_pct_medium.text)
                if _passes_pct_medium
                else None,
                passes_long=cast_to_int(_passes_long.text) if _passes_long else None,
                passes_completed_long=cast_to_int(_passes_completed_long.text)
                if _passes_completed_long
                else None,
                passes_pct_long=cast_to_float(_passes_pct_long.text)
                if _passes_pct_long
                else None,
                assists=cast_to_int(_assists.text) if _assists else None,
                xg_assist=cast_to_float(_xg_assist.text) if _xg_assist else None,
                pass_xa=cast_to_float(_pass_xa.text) if _pass_xa else None,
                assisted_shots=cast_to_int(_assisted_shots.text)
                if _assisted_shots
                else None,
                passes_into_final_third=cast_to_int(_passes_into_final_third.text)
                if _passes_into_final_third
                else None,
                passes_into_penalty_area=cast_to_int(_passes_into_penalty_area.text)
                if _passes_into_penalty_area
                else None,
                crosses_into_penalty_area=cast_to_int(_crosses_into_penalty_area.text)
                if _crosses_into_penalty_area
                else None,
                progressive_passes=cast_to_int(_progressive_passes.text)
                if _progressive_passes
                else None,
            )
        else:
            return None

    def _parse_player_match_pass_types(
        self,
        player: Any,
        league_name: str,
        team_name: str
    ) -> Optional[PlayerMatchStats]:
        if player.find("th", {"data-stat": "player"}) is not None:
            # common
            _player = player.find("th", {"data-stat": "player"})
            if _player is None or _player.get("data-append-csv") is None:
                return None
            _shirt_number = player.find("td", {"data-stat": "shirtnumber"})
            _nationality = player.find("td", {"data-stat": "nationality"})
            _position = player.find("td", {"data-stat": "position"})
            _minutes = player.find("td", {"data-stat": "minutes"})
            # pass types
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

            return PlayerMatchStats(
                # common
                name=_player.text.strip(),
                player_id=_player["data-append-csv"],
                shirt_number=cast_to_int(_shirt_number.text),
                nationality=_nationality.text.split(" ")[-1],
                position=_position.text,
                minutes=cast_to_int(_minutes.text),
                player_url= "https://fbref.com" + _player.find("a").get("href")
                if _player.find("a") is not None and _player.find("a").get("href") is not None
                else None,
                league_name=league_name,
                team_name=team_name,
                # pass types
                passes_live=cast_to_int(_passes_live.text) if _passes_live else None,
                passes_dead=cast_to_int(_passes_dead.text) if _passes_dead else None,
                passes_free_kicks=cast_to_int(_passes_free_kicks.text)
                if _passes_free_kicks
                else None,
                through_balls=cast_to_int(_through_balls.text)
                if _through_balls
                else None,
                passes_switches=cast_to_int(_passes_switches.text)
                if _passes_switches
                else None,
                crosses=cast_to_int(_crosses.text) if _crosses else None,
                throw_ins=cast_to_int(_throw_ins.text) if _throw_ins else None,
                # corner kicks
                corner_kicks=cast_to_int(_corner_kicks.text) if _corner_kicks else None,
                corner_kicks_in=cast_to_int(_corner_kicks_in.text)
                if _corner_kicks_in
                else None,
                corner_kicks_out=cast_to_int(_corner_kicks_out.text)
                if _corner_kicks_out
                else None,
                corner_kicks_straight=cast_to_int(_corner_kicks_straight.text)
                if _corner_kicks_straight
                else None,
                # outcomes
                passes_completed=cast_to_int(_passes_completed.text)
                if _passes_completed
                else None,
                passes_offsides=cast_to_int(_passes_offsides.text)
                if _passes_offsides
                else None,
                passes_blocked=cast_to_int(_passes_blocked.text)
                if _passes_blocked
                else None,
            )
        else:
            return None

    def _parse_player_match_defensive_actions(
        self,
        player: Any,
        league_name: str,
        team_name: str
    ) -> Optional[PlayerMatchStats]:
        if player.find("th", {"data-stat": "player"}) is not None:
            # common
            _player = player.find("th", {"data-stat": "player"})
            if _player is None or _player.get("data-append-csv") is None:
                return None
            _shirt_number = player.find("td", {"data-stat": "shirtnumber"})
            _nationality = player.find("td", {"data-stat": "nationality"})
            _position = player.find("td", {"data-stat": "position"})
            _minutes = player.find("td", {"data-stat": "minutes"})
            # tackles
            _tackles = player.find("td", {"data-stat": "tackles"})
            _tackles_won = player.find("td", {"data-stat": "tackles_won"})
            _tackles_def_3rd = player.find("td", {"data-stat": "tackles_def_3rd"})
            _tackles_mid_3rd = player.find("td", {"data-stat": "tackles_mid_3rd"})
            _tackles_att_3rd = player.find("td", {"data-stat": "tackles_att_3rd"})
            # challenges
            _challenge_tackles = player.find("td", {"data-stat": "challenge_tackles"})
            _challenges = player.find("td", {"data-stat": "challenges"})
            _challenge_tackles_pct = player.find(
                "td", {"data-stat": "challenge_tackles_pct"}
            )
            _challenges_lost = player.find("td", {"data-stat": "challenges_lost"})
            # blocks
            _blocks = player.find("td", {"data-stat": "blocks"})
            _blocked_shots = player.find("td", {"data-stat": "blocked_shots"})
            _blocked_passes = player.find("td", {"data-stat": "blocked_passes"})
            # interceptions
            _interceptions = player.find("td", {"data-stat": "interceptions"})
            _tackles_interceptions = player.find(
                "td", {"data-stat": "tackles_interceptions"}
            )
            _clearances = player.find("td", {"data-stat": "clearances"})
            _errors = player.find("td", {"data-stat": "errors"})

            return PlayerMatchStats(
                # common
                name=_player.text.strip(),
                player_id=_player["data-append-csv"],
                shirt_number=cast_to_int(_shirt_number.text),
                nationality=_nationality.text.split(" ")[-1],
                position=_position.text,
                minutes=cast_to_int(_minutes.text),
                player_url= "https://fbref.com" + _player.find("a").get("href")
                if _player.find("a") is not None and _player.find("a").get("href") is not None
                else None,
                league_name=league_name,
                team_name=team_name,
                # tackles
                tackles=cast_to_int(_tackles.text) if _tackles else None,
                tackles_won=cast_to_int(_tackles_won.text) if _tackles_won else None,
                tackles_def_3rd=cast_to_int(_tackles_def_3rd.text)
                if _tackles_def_3rd
                else None,
                tackles_mid_3rd=cast_to_int(_tackles_mid_3rd.text)
                if _tackles_mid_3rd
                else None,
                tackles_att_3rd=cast_to_int(_tackles_att_3rd.text)
                if _tackles_att_3rd
                else None,
                # challenges
                challenge_tackles=cast_to_int(_challenge_tackles.text)
                if _challenge_tackles
                else None,
                challenges=cast_to_int(_challenges.text) if _challenges else None,
                challenge_tackles_pct=cast_to_float(_challenge_tackles_pct.text)
                if _challenge_tackles_pct
                else None,
                challenges_lost=cast_to_int(_challenges_lost.text)
                if _challenges_lost
                else None,
                # blocks
                blocks=cast_to_int(_blocks.text) if _blocks else None,
                blocked_shots=cast_to_int(_blocked_shots.text)
                if _blocked_shots
                else None,
                blocked_passes=cast_to_int(_blocked_passes.text)
                if _blocked_passes
                else None,
                # interceptions
                interceptions=cast_to_int(_interceptions.text)
                if _interceptions
                else None,
                tackles_interceptions=cast_to_int(_tackles_interceptions.text)
                if _tackles_interceptions
                else None,
                clearances=cast_to_int(_clearances.text) if _clearances else None,
                errors=cast_to_int(_errors.text) if _errors else None,
            )
        else:
            return None

    def _parse_player_match_possession(
        self,
        player: Any,
        league_name: str,
        team_name: str
    ) -> Optional[PlayerMatchStats]:
        if player.find("th", {"data-stat": "player"}) is not None:
            # common
            _player = player.find("th", {"data-stat": "player"})
            if _player is None or _player.get("data-append-csv") is None:
                return None
            _shirt_number = player.find("td", {"data-stat": "shirtnumber"})
            _nationality = player.find("td", {"data-stat": "nationality"})
            _position = player.find("td", {"data-stat": "position"})
            _minutes = player.find("td", {"data-stat": "minutes"})
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
            # receiving
            _passes_received = player.find("td", {"data-stat": "passes_received"})
            _progressive_passes_received = player.find(
                "td", {"data-stat": "progressive_passes_received"}
            )

            return PlayerMatchStats(
                # common
                name=_player.text.strip(),
                player_id=_player["data-append-csv"],
                shirt_number=cast_to_int(_shirt_number.text),
                nationality=_nationality.text.split(" ")[-1],
                position=_position.text,
                minutes=cast_to_int(_minutes.text),
                player_url= "https://fbref.com" + _player.find("a").get("href")
                if _player.find("a") is not None and _player.find("a").get("href") is not None
                else None,
                league_name=league_name,
                team_name=team_name,
                # touches
                touches=cast_to_int(_touches.text) if _touches else None,
                touches_def_pen_area=cast_to_int(_touches_def_pen_area.text)
                if _touches_def_pen_area
                else None,
                touches_def_3rd=cast_to_int(_touches_def_3rd.text)
                if _touches_def_3rd
                else None,
                touches_mid_3rd=cast_to_int(_touches_mid_3rd.text)
                if _touches_mid_3rd
                else None,
                touches_att_3rd=cast_to_int(_touches_att_3rd.text)
                if _touches_att_3rd
                else None,
                touches_att_pen_area=cast_to_int(_touches_att_pen_area.text)
                if _touches_att_pen_area
                else None,
                touches_live_ball=cast_to_int(_touches_live_ball.text)
                if _touches_live_ball
                else None,
                # take_ons
                take_ons=cast_to_int(_take_ons.text) if _take_ons else None,
                take_ons_won=cast_to_int(_take_ons_won.text)
                if _take_ons_won
                else None,
                take_ons_won_pct=cast_to_float(_take_ons_won_pct.text)
                if _take_ons_won_pct
                else None,
                take_ons_tackled=cast_to_int(_take_ons_tackled.text)
                if _take_ons_tackled
                else None,
                take_ons_tackled_pct=cast_to_float(_take_ons_tackled_pct.text)
                if _take_ons_tackled_pct
                else None,
                # carries
                carries=cast_to_int(_carries.text) if _carries else None,
                carries_distance=cast_to_int(_carries_distance.text)
                if _carries_distance
                else None,
                carries_progressive_distance=cast_to_int(
                    _carries_progressive_distance.text
                )
                if _carries_progressive_distance
                else None,
                progressive_carries=cast_to_int(_progressive_carries.text)
                if _progressive_carries
                else None,
                carries_into_final_third=cast_to_int(_carries_into_final_third.text)
                if _carries_into_final_third
                else None,
                carries_into_penalty_area=cast_to_int(_carries_into_penalty_area.text)
                if _carries_into_penalty_area
                else None,
                miscontrols=cast_to_int(_miscontrols.text) if _miscontrols else None,
                dispossessed=cast_to_int(_dispossessed.text) if _dispossessed else None,
                # receiving
                passes_received=cast_to_int(_passes_received.text)
                if _passes_received
                else None,
                progressive_passes_received=cast_to_int(
                    _progressive_passes_received.text
                )
                if _progressive_passes_received
                else None,
            )
        else:
            return None

    def _parse_player_match_miscellaneous(
        self,
        player: Any,
        league_name: str,
        team_name: str
    ) -> Optional[PlayerMatchStats]:
        if player.find("th", {"data-stat": "player"}) is not None:
            # common
            _player = player.find("th", {"data-stat": "player"})
            if _player is None or _player.get("data-append-csv") is None:
                return None
            _shirt_number = player.find("td", {"data-stat": "shirtnumber"})
            _nationality = player.find("td", {"data-stat": "nationality"})
            _position = player.find("td", {"data-stat": "position"})
            _minutes = player.find("td", {"data-stat": "minutes"})
            # performance
            _yellow_cards = player.find("td", {"data-stat": "cards_yellow"})
            _red_cards = player.find("td", {"data-stat": "cards_red"})
            _yellow_red_cards = player.find("td", {"data-stat": "cards_yellow_red"})
            _fouls = player.find("td", {"data-stat": "fouls"})
            _fouled = player.find("td", {"data-stat": "fouled"})
            _offsides = player.find("td", {"data-stat": "offsides"})
            _crosses = player.find("td", {"data-stat": "crosses"})
            _interceptions = player.find("td", {"data-stat": "interceptions"})
            _tackles_won = player.find("td", {"data-stat": "tackles_won"})
            _pens_won = player.find("td", {"data-stat": "pens_won"})
            _pens_conceded = player.find("td", {"data-stat": "pens_conceded"})
            _own_goals = player.find("td", {"data-stat": "own_goals"})
            _ball_recoveries = player.find("td", {"data-stat": "ball_recoveries"})
            # aerial duels
            _aerials_won = player.find("td", {"data-stat": "aerials_won"})
            _aerials_lost = player.find("td", {"data-stat": "aerials_lost"})
            _aerials_won_pct = player.find("td", {"data-stat": "aerials_won_pct"})

            return PlayerMatchStats(
                # common
                name=_player.text.strip(),
                player_id=_player["data-append-csv"],
                shirt_number=cast_to_int(_shirt_number.text),
                nationality=_nationality.text.split(" ")[-1],
                position=_position.text,
                minutes=cast_to_int(_minutes.text),
                player_url= "https://fbref.com" + _player.find("a").get("href")
                if _player.find("a") is not None and _player.find("a").get("href") is not None
                else None,
                league_name=league_name,
                team_name=team_name,
                # performance
                yellow_cards=cast_to_int(_yellow_cards.text) if _yellow_cards else None,
                red_cards=cast_to_int(_red_cards.text) if _red_cards else None,
                yellow_red_cards=cast_to_int(_yellow_red_cards.text)
                if _yellow_red_cards
                else None,
                fouls=cast_to_int(_fouls.text) if _fouls else None,
                fouled=cast_to_int(_fouled.text) if _fouled else None,
                offsides=cast_to_int(_offsides.text) if _offsides else None,
                crosses=cast_to_int(_crosses.text) if _crosses else None,
                interceptions=cast_to_int(_interceptions.text)
                if _interceptions
                else None,
                tackles_won=cast_to_int(_tackles_won.text) if _tackles_won else None,
                pens_won=cast_to_int(_pens_won.text) if _pens_won else None,
                pens_conceded=cast_to_int(_pens_conceded.text)
                if _pens_conceded
                else None,
                own_goals=cast_to_int(_own_goals.text) if _own_goals else None,
                ball_recoveries=cast_to_int(_ball_recoveries.text)
                if _ball_recoveries
                else None,
                # aerial duels
                aerials_won=cast_to_int(_aerials_won.text) if _aerials_won else None,
                aerials_lost=cast_to_int(_aerials_lost.text) if _aerials_lost else None,
                aerials_won_pct=cast_to_float(_aerials_won_pct.text)
                if _aerials_won_pct
                else None,
            )
        else:
            return None

    def _parse_player_match_goalkeeper(
        self,
        player: Any,
        league_name: str,
        team_name: str
    ) -> Optional[PlayerMatchStats]:
        if player.find("th", {"data-stat": "player"}) is not None:
            # common
            _player = player.find("th", {"data-stat": "player"})
            if _player is None or _player.get("data-append-csv") is None:
                return None
            _nationality = player.find("td", {"data-stat": "nationality"})
            _minutes = player.find("td", {"data-stat": "minutes"})
            # shot stopping
            _gk_shots_on_target_against = player.find(
                "td", {"data-stat": "gk_shots_on_target_against"}
            )
            _gk_goals_against = player.find("td", {"data-stat": "gk_goals_against"})
            _gk_saves = player.find("td", {"data-stat": "gk_saves"})
            _gk_save_pct = player.find("td", {"data-stat": "gk_save_pct"})
            _gk_psxg = player.find("td", {"data-stat": "gk_psxg"})
            # launched
            _gk_passes_completed_launched = player.find(
                "td", {"data-stat": "gk_passes_completed_launched"}
            )
            _gk_passes_launched = player.find("td", {"data-stat": "gk_passes_launched"})
            _gk_passes_pct_launched = player.find(
                "td", {"data-stat": "gk_passes_pct_launched"}
            )
            # passes
            _gk_passes = player.find("td", {"data-stat": "gk_passes"})
            _gk_passes_throws = player.find("td", {"data-stat": "gk_passes_throws"})
            _gk_pct_passes_launched = player.find(
                "td", {"data-stat": "gk_pct_passes_launched"}
            )
            _gk_passes_length_avg = player.find(
                "td", {"data-stat": "gk_passes_length_avg"}
            )
            # goals kicks
            _gk_goal_kicks = player.find("td", {"data-stat": "gk_goal_kicks"})
            _gk_pct_goal_kicks_launched = player.find(
                "td", {"data-stat": "gk_pct_goal_kicks_launched"}
            )
            _gk_goal_kick_length_avg = player.find(
                "td", {"data-stat": "gk_goal_kick_length_avg"}
            )
            # crosses
            _gk_crosses = player.find("td", {"data-stat": "gk_crosses"})
            _gk_crosses_stopped = player.find("td", {"data-stat": "gk_crosses_stopped"})
            _gk_crosses_stopped_pct = player.find(
                "td", {"data-stat": "gk_crosses_stopped_pct"}
            )
            # sweeper
            _gk_def_actions_outside_pen_area = player.find(
                "td", {"data-stat": "gk_def_actions_outside_pen_area"}
            )
            _gk_avg_distance_def_actions = player.find(
                "td", {"data-stat": "gk_avg_distance_def_actions"}
            )

            return PlayerMatchStats(
                # common
                name=_player.text.strip(),
                player_id=_player["data-append-csv"],
                nationality=_nationality.text.split(" ")[-1],
                minutes=cast_to_int(_minutes.text),
                player_url= "https://fbref.com" + _player.find("a").get("href")
                if _player.find("a") is not None and _player.find("a").get("href") is not None
                else None,
                league_name=league_name,
                team_name=team_name,
                # shot stopping
                gk_shots_on_target_against=cast_to_int(
                    _gk_shots_on_target_against.text
                )
                if _gk_shots_on_target_against
                else None,
                gk_goals_against=cast_to_int(_gk_goals_against.text)
                if _gk_goals_against
                else None,
                gk_saves=cast_to_int(_gk_saves.text) if _gk_saves else None,
                gk_save_pct=cast_to_float(_gk_save_pct.text)
                if _gk_save_pct
                else None,
                gk_psxg=cast_to_float(_gk_psxg.text) if _gk_psxg else None,
                # launched
                gk_passes_completed_launched=cast_to_int(
                    _gk_passes_completed_launched.text
                )
                if _gk_passes_completed_launched
                else None,
                gk_passes_launched=cast_to_int(_gk_passes_launched.text)
                if _gk_passes_launched
                else None,
                gk_passes_pct_launched=cast_to_float(
                    _gk_passes_pct_launched.text
                )
                if _gk_passes_pct_launched
                else None,
                # passes
                gk_passes=cast_to_int(_gk_passes.text) if _gk_passes else None,
                gk_passes_throws=cast_to_int(_gk_passes_throws.text)
                if _gk_passes_throws
                else None,
                gk_pct_passes_launched=cast_to_float(
                    _gk_pct_passes_launched.text
                )
                if _gk_pct_passes_launched
                else None,
                gk_passes_length_avg=cast_to_float(_gk_passes_length_avg.text)
                if _gk_passes_length_avg
                else None,
                # goals kicks
                gk_goal_kicks=cast_to_int(_gk_goal_kicks.text)
                if _gk_goal_kicks
                else None,
                gk_pct_goal_kicks_launched=cast_to_float(
                    _gk_pct_goal_kicks_launched.text
                )
                if _gk_pct_goal_kicks_launched
                else None,
                gk_goal_kick_length_avg=cast_to_float(
                    _gk_goal_kick_length_avg.text
                )
                if _gk_goal_kick_length_avg
                else None,
                # crosses
                gk_crosses=cast_to_int(_gk_crosses.text) if _gk_crosses else None,
                gk_crosses_stopped=cast_to_int(_gk_crosses_stopped.text)
                if _gk_crosses_stopped
                else None,
                gk_crosses_stopped_pct=cast_to_float(
                    _gk_crosses_stopped_pct.text
                )
                if _gk_crosses_stopped_pct
                else None,
                # sweeper
                gk_def_actions_outside_pen_area=cast_to_int(
                    _gk_def_actions_outside_pen_area.text
                )
                if _gk_def_actions_outside_pen_area
                else None,
                gk_avg_distance_def_actions=cast_to_float(
                    _gk_avg_distance_def_actions.text
                )
                if _gk_avg_distance_def_actions
                else None
            )
        else:
            return None

    def _parse_match_summary_stats(
        self, parsed_table: Any, team_id: str, league_name: str
    ) -> List[PlayerStats]:
        result = []

        section_anchor = parsed_table.find("div", {"class": f"assoc_stats_{team_id}_summary"})
        if section_anchor is None:
            return result
        team_name = section_anchor.text.split("Player Stats")[0].strip()
        summary_table = parsed_table.find("div", {"id": f"div_stats_{team_id}_summary"})

        if summary_table is not None:
            summary_rows = summary_table.find_all("tr")
            if len(summary_rows) > 2:
                for row in summary_rows[2:]:
                    player_stats = self._parse_player_match_summary_stat(
                        player=row,
                        league_name=league_name,
                        team_name=team_name
                    )
                    if player_stats is not None:
                        result.append(player_stats)

        return result

    def _parse_match_passing_stats(
        self, parsed_table: Any, team_id: str, league_name: str
    ) -> List[PlayerMatchStats]:
        result = []

        section_anchor = parsed_table.find("div", {"class": f"assoc_stats_{team_id}_passing"})
        if section_anchor is None:
            return result
        team_name = section_anchor.text.split("Player Stats")[0].strip()
        passing_table = parsed_table.find("div", {"id": f"div_stats_{team_id}_passing"})

        if passing_table is not None:
            passing_rows = passing_table.find_all("tr")
            if len(passing_rows) > 2:
                for row in passing_rows[2:]:
                    player_stats = self._parse_player_match_passing_stat(
                        player=row,
                        league_name=league_name,
                        team_name=team_name
                    )
                    if player_stats is not None:
                        result.append(player_stats)

        return result

    def _parse_match_pass_types_stats(
        self, parsed_table: Any, team_id: str, league_name: str
    ) -> List[PlayerMatchStats]:
        result = []

        section_anchor = parsed_table.find("div", {"class": f"assoc_stats_{team_id}_passing_types"})
        if section_anchor is None:
            return result
        team_name = section_anchor.text.split("Player Stats")[0].strip()
        pass_types_table = parsed_table.find("div", {"id": f"div_stats_{team_id}_passing_types"})
    
        if pass_types_table is not None:
            passing_rows = pass_types_table.find_all("tr")
            if len(passing_rows) > 2:
                for row in passing_rows[2:]:
                    player_stats = self._parse_player_match_pass_types(
                        player=row,
                        league_name=league_name,
                        team_name=team_name
                    )
                    if player_stats is not None:
                        result.append(player_stats)

        return result

    def _parse_match_defensive_actions_stats(
        self, parsed_table: Any, team_id: str, league_name: str
    ) -> List[PlayerMatchStats]:
        result = []

        section_anchor = parsed_table.find("div", {"class": f"assoc_stats_{team_id}_defense"})
        if section_anchor is None:
            return result
        team_name = section_anchor.text.split("Player Stats")[0].strip()
        defensive_actions_table = parsed_table.find("div", {"id": f"div_stats_{team_id}_defense"})
    
        if defensive_actions_table is not None:
            defensive_actions_rows = defensive_actions_table.find_all("tr")
            if len(defensive_actions_rows) > 2:
                for row in defensive_actions_rows[2:]:
                    player_stats = self._parse_player_match_defensive_actions(
                        player=row,
                        league_name=league_name,
                        team_name=team_name
                    )
                    if player_stats is not None:
                        result.append(player_stats)

        return result

    def _parse_match_possesions_stats(
        self, parsed_table: Any, team_id: str, league_name: str
    ) -> List[PlayerMatchStats]:
        result = []

        section_anchor = parsed_table.find("div", {"class": f"assoc_stats_{team_id}_possession"})
        if section_anchor is None:
            return result
        team_name = section_anchor.text.split("Player Stats")[0].strip()
        possessions_table = parsed_table.find("div", {"id": f"div_stats_{team_id}_possession"})
    
        if possessions_table is not None:
            possessions_rows = possessions_table.find_all("tr")
            if len(possessions_rows) > 2:
                for row in possessions_rows[2:]:
                    player_stats = self._parse_player_match_possession(
                        player=row,
                        league_name=league_name,
                        team_name=team_name
                    )
                    if player_stats is not None:
                        result.append(player_stats)

        return result

    def _parse_match_miscellaneous_stats(
        self, parsed_table: Any, team_id: str, league_name: str
    ) -> List[PlayerMatchStats]:
        result = []

        section_anchor = parsed_table.find("div", {"class": f"assoc_stats_{team_id}_misc"})
        if section_anchor is None:
            return result
        team_name = section_anchor.text.split("Player Stats")[0].strip()
        miscellaneous_table = parsed_table.find("div", {"id": f"div_stats_{team_id}_misc"})
    
        if miscellaneous_table is not None:
            miscellaneous_rows = miscellaneous_table.find_all("tr")
            if len(miscellaneous_rows) > 2:
                for row in miscellaneous_rows[2:]:
                    player_stats = self._parse_player_match_miscellaneous(
                        player=row,
                        league_name=league_name,
                        team_name=team_name
                    )
                    if player_stats is not None:
                        result.append(player_stats)

        return result

    def _parse_match_goalkeeper_stats(
        self, parsed_table: Any, team_id: str, league_name: str
    ) -> List[PlayerMatchStats]:
        result = []

        section_anchor = parsed_table.find("div", {"class": f"assoc_keeper_stats_{team_id}"})
        if section_anchor is None:
            return result
        team_name = section_anchor.text.split("Goalkeeper Stats")[0].strip()
        goalkeeper_table = parsed_table.find("div", {"id": f"div_keeper_stats_{team_id}"})
    
        if goalkeeper_table is not None:
            goalkeeper_rows = goalkeeper_table.find_all("tr")
            if len(goalkeeper_rows) > 2:
                for row in goalkeeper_rows[2:]:
                    player_stats = self._parse_player_match_goalkeeper(
                        player=row,
                        league_name=league_name,
                        team_name=team_name
                    )
                    if player_stats is not None:
                        result.append(player_stats)

        return result

    def _parse_match_stats_tables(
        self, 
        league_name: str, 
        main_table: WebElement,
        goalkeeper_table: WebElement
    ) -> List[PlayerStats]:
        table_id = main_table.get_attribute("id")
        team_id = table_id.split("_")[-1]
        parsed_main_table = BeautifulSoup(
            main_table.get_attribute("outerHTML"), "html.parser"
        )
        if not parsed_main_table:
            return []

        players = {}
        # summary stats
        players_stats = self._parse_match_summary_stats(
            parsed_main_table, 
            team_id,
            league_name
        )
        players = self._update_players_match_stat(players, players_stats)
        # passing stats
        players_stats = self._parse_match_passing_stats(
            parsed_main_table, 
            team_id,
            league_name
        )
        players = self._update_players_match_stat(players, players_stats)
        # pass types stats
        players_stats = self._parse_match_pass_types_stats(
            parsed_main_table, 
            team_id,
            league_name
        )
        players = self._update_players_match_stat(players, players_stats)
        # defensive actions stats
        players_stats = self._parse_match_defensive_actions_stats(
            parsed_main_table, 
            team_id,
            league_name
        )
        players = self._update_players_match_stat(players, players_stats)
        # possession stats
        players_stats = self._parse_match_possesions_stats(
            parsed_main_table, 
            team_id,
            league_name
        )
        players = self._update_players_match_stat(players, players_stats)
        # miscellaneous stats
        players_stats = self._parse_match_miscellaneous_stats(
            parsed_main_table, 
            team_id,
            league_name
        )
        players = self._update_players_match_stat(players, players_stats)

        parsed_goalkeeper_table = BeautifulSoup(
            goalkeeper_table.get_attribute("outerHTML"), "html.parser"
        )
        if not parsed_goalkeeper_table:
            return list(players.values())
        
        players_stats = self._parse_match_goalkeeper_stats(
            parsed_goalkeeper_table, 
            team_id,
            league_name
        )
        players = self._update_players_match_stat(players, players_stats)

        return list(players.values())

    def parse_match_stats(self, match_url: str, league_name: str) -> List[PlayerMatchStats]:
        driver = None
        try:
            opts = FirefoxOptions()
            opts.add_argument("--headless")
            opts.add_argument("--disable-blink-features=AutomationControlled")

            driver = webdriver.Firefox(
                executable_path=os.environ["GECKODRIVER_PATH"], options=opts
            )
            driver.get(match_url)
            all_stats_tables: List[WebElement] = WebDriverWait(driver, 3).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "table_wrapper"))
            )
            if len(all_stats_tables) < 4:
                return []

            players = []
            players += self._parse_match_stats_tables(
                league_name, 
                all_stats_tables[0],
                all_stats_tables[1]
            )
            players += self._parse_match_stats_tables(
                league_name, 
                all_stats_tables[2],
                all_stats_tables[3]
            )
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            logging.warning(f"Ex={ex} in file={fname} line={exc_tb.tb_lineno}")
            logging.warning(f"match_url={match_url}")
            return []
        else:
            return players
        finally:
            if driver is not None:
                driver.quit()

    def get_stats_league(self, league_name: str) -> List[PlayerStats]:
        players: Dict[Tuple[str, str, str, str], PlayerStats] = {}
        # playing time stats
        if league_name in self._playing_time_leagues:
            url = self._playing_time_leagues[league_name]
            playing_time_players = self._parse_league_stats(
                league_name=league_name,
                url=url,
                table_name="stats_playing_time",
                parse_func=self._parse_player_playing_time_stat,
            )
            players = self._update_players_stat(players, playing_time_players)
        # standart stats
        if league_name in self._standart_leagues:
            url = self._standart_leagues[league_name]
            standart_players = self._parse_league_stats(
                league_name=league_name,
                url=url,
                table_name="stats_standard",
                parse_func=self._parse_player_standart_stat,
            )
            players = self._update_players_stat(players, standart_players)
        # shooting stats
        if league_name in self._shooting_leagues:
            url = self._shooting_leagues[league_name]
            shooting_players = self._parse_league_stats(
                league_name=league_name,
                url=url,
                table_name="stats_shooting",
                parse_func=self._parse_player_shooting_stat,
            )
            players = self._update_players_stat(players, shooting_players)
        # passing stats
        if league_name in self._passing_leagues:
            url = self._passing_leagues[league_name]
            passing_players = self._parse_league_stats(
                league_name=league_name,
                url=url,
                table_name="stats_passing",
                parse_func=self._parse_player_passing_stat,
            )
            players = self._update_players_stat(players, passing_players)
        # pass types stats
        if league_name in self._pass_types_leagues:
            url = self._pass_types_leagues[league_name]
            pass_types_players = self._parse_league_stats(
                league_name=league_name,
                url=url,
                table_name="stats_passing_types",
                parse_func=self._parse_player_pass_types_stat,
            )
            players = self._update_players_stat(players, pass_types_players)
        # possession stats
        if league_name in self._possession_leagues:
            url = self._possession_leagues[league_name]
            possession_players = self._parse_league_stats(
                league_name=league_name,
                url=url,
                table_name="stats_possession",
                parse_func=self._parse_player_possession_stat,
            )
            players = self._update_players_stat(players, possession_players)
        # shot creation stats
        if league_name in self._shot_creation_leagues:
            url = self._shot_creation_leagues[league_name]
            shot_creation_players = self._parse_league_stats(
                league_name=league_name,
                url=url,
                table_name="stats_gca",
                parse_func=self._parse_player_shot_creation_stat,
            )
            players = self._update_players_stat(players, shot_creation_players)
        return list(players.values())

    def get_all_leagues(self) -> List[str]:
        all_leagues: List[str] = []
        for leagues_dict in [
            self._playing_time_leagues,
            self._standart_leagues,
            self._shooting_leagues,
            self._passing_leagues,
            self._pass_types_leagues,
            self._possession_leagues,
            self._shot_creation_leagues,
        ]:
            all_leagues.extend(league_name for league_name in leagues_dict.keys())
        return list(set(all_leagues))
