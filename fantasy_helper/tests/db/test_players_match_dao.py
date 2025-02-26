import datetime
from typing import List
import os.path as path
import sys

import pytest

from fantasy_helper.tests.fixtures import leagues
from fantasy_helper.db.dao.players_match import PlayersMatchDao
from fantasy_helper.utils.dataclasses import LeagueInfo


@pytest.fixture
def dao(leagues: List[LeagueInfo]) -> PlayersMatchDao:
    return PlayersMatchDao(leagues)


def test_get_players_match_stats(leagues: List[LeagueInfo], dao: PlayersMatchDao):
    for league in leagues:
        league_players = dao.get_players_match_stats(league.name)
        print(len(league_players))
        print(league_players[0])
        assert len(league_players) > 0
        # assert False


def test_get_players_stats_info(leagues: List[LeagueInfo], dao: PlayersMatchDao):
    for league in leagues:
        league_players = dao.get_players_stats_info(league.name)
        print(len(league_players))
        for player in league_players:
            if player.name == "Konstantinos Mavropanos":
                print()
                print(player)
        assert len(league_players) > 0
        assert False
