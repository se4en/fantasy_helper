import datetime
from typing import List
import os.path as path
import sys

import pytest

from fantasy_helper.tests.fixtures import leagues
from fantasy_helper.parsers.fbref import FbrefParser
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo, SportsPlayerStats


@pytest.fixture
def parser(leagues: List[LeagueInfo]) -> FbrefParser:
    return FbrefParser(leagues)


def test_league_table_basic(leagues: List[LeagueInfo], parser: FbrefParser):
    for league in leagues:
        league_table = parser._parse_league_table(league.name)
        assert len(league_table) > 0

def test_league_schedule_basic(leagues: List[LeagueInfo], parser: FbrefParser):
    for league in leagues:
        league_schedule = parser.get_league_schedule(league.name)
        print(league_schedule)
        assert False
        assert len(league_schedule) > 0
