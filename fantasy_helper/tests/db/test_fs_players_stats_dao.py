import datetime
from typing import List
import os.path as path
import sys

import pytest

from fantasy_helper.tests.fixtures import leagues
from fantasy_helper.db.dao.feature_store.fs_players_stats import FSPlayersStatsDAO
from fantasy_helper.utils.dataclasses import LeagueInfo


@pytest.fixture
def dao() -> FSPlayersStatsDAO:
    return FSPlayersStatsDAO()


def test_get_players_stats_info(leagues: List[LeagueInfo], dao: FSPlayersStatsDAO):
    for league in leagues:
        league_players = dao.get_players_stats_info(league.name)
        assert len(league_players) > 0
