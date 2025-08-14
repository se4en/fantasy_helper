from typing import List

import pytest
import pytest_asyncio

from fantasy_helper.tests.fixtures import leagues
from fantasy_helper.parsers.betcity import BetcityParser
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


@pytest_asyncio.fixture
def parser(leagues: List[LeagueInfo]) -> BetcityParser:
    return BetcityParser(leagues)


@pytest.mark.asyncio
async def test_empty_matches(leagues: List[LeagueInfo], parser: BetcityParser):
    for league in leagues:
        matches = await parser.get_league_matches(league.name)
        assert len(matches) > 0
        assert False
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
