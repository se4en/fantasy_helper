import datetime
from typing import List
import os.path as path
import sys

import pytest

from fantasy_helper.tests.fixtures import leagues
from fantasy_helper.parsers.mole import MoleParser
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo, SportsPlayerStats


@pytest.fixture
def parser(leagues: List[LeagueInfo]) -> MoleParser:
    return MoleParser(leagues)


def test_lineup_basic(parser: MoleParser):
    all_lineups = parser.get_lineups()
    assert len(all_lineups) > 0
