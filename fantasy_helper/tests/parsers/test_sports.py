import datetime
from typing import List
import os.path as path

import pytest

from fantasy_helper.tests.fixtures import leagues
from fantasy_helper.parsers.sports import SportsParser
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


@pytest.fixture
def parser(leagues: List[LeagueInfo]) -> SportsParser:
    return SportsParser(
        leagues=leagues,
        queries_path=path.join(path.dirname(__file__), "../../parsers/queries"),
    )


def test_empty_cur_tour_info(leagues: List[LeagueInfo], parser: SportsParser):
    for league in leagues:
        info = parser.get_cur_tour_info(league.name)
        assert "number" in info and info["number"] is not None and info["number"] > 0
        assert (
            "matches_count" in info
            and info["matches_count"] is not None
            and info["matches_count"] > 0
        )
        assert isinstance(info["deadline"], datetime.datetime)
