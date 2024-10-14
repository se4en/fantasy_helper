import datetime
from typing import List
import os.path as path

import pytest

from fantasy_helper.tests.fixtures import leagues
from fantasy_helper.parsers.sports import SportsParser
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo, SportsPlayerStats, SportsTourInfo


@pytest.fixture
def parser(leagues: List[LeagueInfo]) -> SportsParser:
    return SportsParser(
        leagues=leagues,
        queries_path=path.join(path.dirname(__file__), "../../parsers/queries"),
    )


def test_basic_current_tour_info(leagues: List[LeagueInfo], parser: SportsParser):
    for league in leagues:
        current_tour = parser.get_current_tour(league.name)
        assert current_tour is not None and current_tour.number > 0
        assert current_tour.matches_count is not None and current_tour.matches_count > 0
        assert isinstance(current_tour.deadline, datetime.datetime)


def test_basic_players_stats_info(leagues: List[LeagueInfo], parser: SportsParser):
    for league in leagues:
        players = parser.get_players_stats_info(league.name)
        assert players is not None
        assert isinstance(players, list)
        assert len(players) > 0
        assert isinstance(players[0], SportsPlayerStats)


def test_basic_schedule_info(leagues: List[LeagueInfo], parser: SportsParser):
    for league in leagues:
        schedule = parser.get_schedule(league.name)
        assert schedule is not None
        assert isinstance(schedule, list)
        assert len(schedule) > 0
        assert isinstance(schedule[0], SportsTourInfo)
