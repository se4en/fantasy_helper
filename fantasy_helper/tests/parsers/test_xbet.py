from typing import List

import pytest

from fantasy_helper.tests.fixtures import leagues
from fantasy_helper.parsers.xbet import XbetParser
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


@pytest.fixture
def parser(leagues: List[LeagueInfo]) -> XbetParser:
    return XbetParser(leagues)


def test_empty_matches(leagues: List[LeagueInfo], parser: XbetParser):
    for league in leagues:
        matches = parser.get_league_matches(league.name)
        assert len(matches) > 0
        for match in matches:
            assert isinstance(match, MatchInfo)
            assert match.away_team is not None and match.away_team != ""
            assert match.home_team is not None and match.home_team != ""
            assert match.url is not None and match.url != ""
            assert (
                match.total_1_over_1_5 is not None
                or match.total_1_under_0_5 is not None
                or match.total_2_over_1_5 is not None
                or match.total_2_under_0_5 is not None
            )
