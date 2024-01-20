import requests
import pytest

from fantasy_helper.tests.api.fixtures import api_url
from fantasy_helper.utils.dataclasses import PlayersLeagueStats


def test_ok_response(api_url: str):
    league_name = "Russia"

    response = requests.get(api_url + f"/players_stats/?league_name={league_name}")
    assert response.status_code == 200


def test_valid_type_of_content(api_url: str):
    league_name = "Russia"

    response = requests.get(api_url + f"/players_stats/?league_name={league_name}")
    assert response.status_code == 200
    content = PlayersLeagueStats()
    content.from_json(response.json())
    assert True
