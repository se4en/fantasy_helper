import datetime
from typing import List
import os.path as path
import sys
from unittest.mock import Mock, patch

import pytest

from fantasy_helper.tests.fixtures import leagues
from fantasy_helper.db.dao.feature_store.fs_players_stats import FSPlayersStatsDAO
from fantasy_helper.utils.dataclasses import LeagueInfo, PlayerStatsInfo, PlayersTableRow


@pytest.fixture
def dao() -> FSPlayersStatsDAO:
    return FSPlayersStatsDAO()


@pytest.fixture
def sample_player_stats() -> List[PlayerStatsInfo]:
    """Create sample player stats for testing."""
    return [
        PlayerStatsInfo(
            name="Player 1",
            team="Team A",
            position="FORWARD",
            games=5,
            games_all=10,
            minutes=450,
            goals=3,
            shots=15,
            shots_on_target=8,
            average_shot_distance=18.5,
            xg=2.1,
            xg_np=1.8,
            xg_xa=3.2,
            xg_np_xa=2.9,
            assists=2,
            xa=1.1,
            key_passes=12,
            passes_into_penalty_area=8,
            crosses_into_penalty_area=4,
            touches_in_attacking_third=45,
            touches_in_attacking_penalty_area=12,
            carries_in_attacking_third=23,
            carries_in_attacking_penalty_area=8,
            sca=6,
            gca=2,
            sports_team="Sports Team A",
            sports_name="Sports Player 1",
            role="FORWARD",
            price=8.5,
            percent_ownership=25.3,
            percent_ownership_diff=2.1
        ),
        PlayerStatsInfo(
            name="Player 2",
            team="Team B",
            position="MIDFIELDER",
            games=8,
            games_all=10,
            minutes=720,
            goals=1,
            shots=8,
            shots_on_target=3,
            average_shot_distance=22.0,
            xg=0.9,
            xg_np=0.9,
            xg_xa=2.5,
            xg_np_xa=2.5,
            assists=4,
            xa=1.6,
            key_passes=18,
            passes_into_penalty_area=15,
            crosses_into_penalty_area=8,
            touches_in_attacking_third=78,
            touches_in_attacking_penalty_area=18,
            carries_in_attacking_third=42,
            carries_in_attacking_penalty_area=12,
            sca=12,
            gca=3,
            sports_team="Sports Team B",
            sports_name="Sports Player 2",
            role="MIDFIELDER",
            price=7.0,
            percent_ownership=15.8,
            percent_ownership_diff=-1.2
        ),
        PlayerStatsInfo(
            name="Player 3",
            team="Team A",
            position="DEFENDER",
            games=3,
            games_all=5,
            minutes=180,
            goals=0,
            shots=1,
            shots_on_target=0,
            average_shot_distance=25.0,
            xg=0.1,
            xg_np=0.1,
            xg_xa=0.5,
            xg_np_xa=0.5,
            assists=1,
            xa=0.4,
            key_passes=3,
            passes_into_penalty_area=2,
            crosses_into_penalty_area=1,
            touches_in_attacking_third=12,
            touches_in_attacking_penalty_area=2,
            carries_in_attacking_third=8,
            carries_in_attacking_penalty_area=1,
            sca=2,
            gca=0,
            sports_team="Sports Team A",
            sports_name="Sports Player 3",
            role="DEFENDER",
            price=4.5,
            percent_ownership=8.2,
            percent_ownership_diff=0.5
        )
    ]


def test_get_players_stats_info(leagues: List[LeagueInfo], dao: FSPlayersStatsDAO):
    for league in leagues:
        league_players = dao.get_players_stats_info(league.name)
        assert len(league_players) > 0


class TestGetPlayersTableRows:
    """Test class for get_players_table_rows method."""
    
    def test_get_players_table_rows_basic_functionality(
        self, dao: FSPlayersStatsDAO, sample_player_stats: List[PlayerStatsInfo]
    ):
        """Test basic functionality of get_players_table_rows method."""
        with patch.object(dao, 'get_players_stats_info', return_value=sample_player_stats):
            result = dao.get_players_table_rows(
                league_name="Russia",
                games_count=10
            )
            
            assert isinstance(result, list)
            assert len(result) == 2
            assert all(isinstance(row, PlayersTableRow) for row in result)
            
            for row in result:
                assert row.league_name == "Russia"
                assert row.name is not None
                assert row.team_name is not None

    def test_get_players_table_rows_empty_data(self, dao: FSPlayersStatsDAO):
        """Test behavior with empty player stats."""
        with patch.object(dao, 'get_players_stats_info', return_value=[]):
            result = dao.get_players_table_rows(
                league_name="Russia",
                games_count=10
            )

            assert result is None

    def test_get_players_table_rows_with_min_minutes_filter(
        self, dao: FSPlayersStatsDAO, sample_player_stats: List[PlayerStatsInfo]
    ):
        """Test filtering by minimum minutes."""
        with patch.object(dao, 'get_players_stats_info', return_value=sample_player_stats):
            result = dao.get_players_table_rows(
                league_name="Russia",
                games_count=10,
                min_minutes=300
            )
            
            # Should filter out Player 3 who has only 180 minutes
            assert len(result) == 2
            player_names = [row.name for row in result]
            assert "Sports Player 1" in player_names
            assert "Sports Player 2" in player_names
            assert "Sports Player 3" not in player_names

    def test_get_players_table_rows_with_normalize_minutes(
        self, dao: FSPlayersStatsDAO, sample_player_stats: List[PlayerStatsInfo]
    ):
        """Test normalization by minutes."""
        with patch.object(dao, 'get_players_stats_info', return_value=sample_player_stats):
            result = dao.get_players_table_rows(
                league_name="Russia",
                games_count=10,
                normalize_minutes=True
            )
            
            assert len(result) == 3
            assert all(isinstance(row, PlayersTableRow) for row in result)

    def test_get_players_table_rows_with_normalize_matches(
        self, dao: FSPlayersStatsDAO, sample_player_stats: List[PlayerStatsInfo]
    ):
        """Test normalization by matches."""
        with patch.object(dao, 'get_players_stats_info', return_value=sample_player_stats):
            result = dao.get_players_table_rows(
                league_name="Russia",
                games_count=10,
                normalize_matches=True
            )

            assert len(result) == 3
            assert all(isinstance(row, PlayersTableRow) for row in result)

    def test_get_players_table_rows_with_games_count_filter(
        self, dao: FSPlayersStatsDAO, sample_player_stats: List[PlayerStatsInfo]
    ):
        """Test filtering by games count."""
        with patch.object(dao, 'get_players_stats_info', return_value=sample_player_stats):
            result = dao.get_players_table_rows(
                league_name="Russia",
                games_count=5  # Lower than max games_all
            )

            assert len(result) == 1
            assert result[0].name == "Sports Player 3"

    def test_get_players_table_rows_position_mapping(
        self, dao: FSPlayersStatsDAO, sample_player_stats: List[PlayerStatsInfo]
    ):
        """Test that position mapping is applied correctly."""
        with patch.object(dao, 'get_players_stats_info', return_value=sample_player_stats):
            result = dao.get_players_table_rows(
                league_name="Russia",
                games_count=10
            )
            
            # Check that role field contains mapped positions
            roles = [row.role for row in result if row.role is not None]
            # The actual mapping converts to Russian abbreviations
            assert any(role in ["нп", "пз", "зщ", "вр"] for role in roles)

    def test_get_players_table_rows_filters_null_sports_name(
        self, dao: FSPlayersStatsDAO
    ):
        """Test that players with null sports_name are filtered out."""
        player_stats_with_null = [
            PlayerStatsInfo(
                name="Player Without Sports Name",
                team="Team A",
                position="FORWARD",
                games=5,
                games_all=10,
                minutes=450,
                goals=3,
                shots=15,
                shots_on_target=8,
                average_shot_distance=18.5,
                xg=2.1,
                xg_np=1.8,
                xg_xa=3.2,
                xg_np_xa=2.9,
                assists=2,
                xa=1.1,
                key_passes=12,
                passes_into_penalty_area=8,
                crosses_into_penalty_area=4,
                touches_in_attacking_third=45,
                touches_in_attacking_penalty_area=12,
                carries_in_attacking_third=23,
                carries_in_attacking_penalty_area=8,
                sca=6,
                gca=2,
                sports_team="Sports Team A",
                sports_name=None,  # This should be filtered out
                role="FORWARD",
                price=8.5,
                percent_ownership=25.3,
                percent_ownership_diff=2.1
            )
        ]
        
        with patch.object(dao, 'get_players_stats_info', return_value=player_stats_with_null):
            result = dao.get_players_table_rows(
                league_name="Russia",
                games_count=10
            )
            
            # Should filter out player with null sports_name
            assert len(result) == 0

    def test_get_players_table_rows_all_parameters(
        self, dao: FSPlayersStatsDAO, sample_player_stats: List[PlayerStatsInfo]
    ):
        """Test with all parameters specified."""
        with patch.object(dao, 'get_players_stats_info', return_value=sample_player_stats):
            result = dao.get_players_table_rows(
                league_name="Russia",
                games_count=10,
                normalize_minutes=False,
                normalize_matches=False,
                min_minutes=100
            )
            
            # Should return all players that meet criteria
            assert len(result) == 3
            assert all(isinstance(row, PlayersTableRow) for row in result)
            
            # Verify all required fields are populated
            for row in result:
                assert row.player_id is not None
                assert row.league_name == "Russia"
                assert row.name is not None
                assert row.team_name is not None

    def test_get_players_table_rows_stats_preservation(
        self, dao: FSPlayersStatsDAO, sample_player_stats: List[PlayerStatsInfo]
    ):
        """Test that statistical data is preserved in the output."""
        with patch.object(dao, 'get_players_stats_info', return_value=sample_player_stats):
            result = dao.get_players_table_rows(
                league_name="Russia",
                games_count=10
            )
            
            # Should preserve statistical data
            assert len(result) == 3
            
            # Find Player 1 result
            player_1_result = next((row for row in result if row.name == "Sports Player 1"), None)
            assert player_1_result is not None
            assert player_1_result.goals == 3
            assert player_1_result.assists == 2
            assert player_1_result.minutes == 450
