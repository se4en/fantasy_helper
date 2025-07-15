from typing import List

import pytest
import pytest_asyncio

from fantasy_helper.tests.fixtures import leagues
from fantasy_helper.parsers.marathon import MarathonParser
from fantasy_helper.utils.dataclasses import LeagueInfo, MatchInfo


@pytest_asyncio.fixture
async def parser(leagues: List[LeagueInfo]) -> MarathonParser:
    return MarathonParser(leagues)


@pytest.mark.asyncio
async def test_empty_matches(leagues: List[LeagueInfo], parser: MarathonParser):
    for league in leagues:
        if league.marathon_url is None:
            continue
        matches = await parser.get_league_matches(league.name)
        assert len(matches) > 0
        for match in matches:
            assert isinstance(match, MatchInfo)
            assert match.away_team is not None and match.away_team != ""
            assert match.home_team is not None and match.home_team != ""
            assert match.url is not None and match.url != ""
