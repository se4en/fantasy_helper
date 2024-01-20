import requests
import pytest

from fantasy_helper.tests.api.fixtures import api_url
from fantasy_helper.utils.dataclasses import PlayersLeagueStats


def test_ok_response(api_url: str):
    """
    Function to test the response of an API endpoint that is expected to return a 200 status code.

    Args:
        api_url (str): The URL of the API endpoint.

    Returns:
        None
    """
    league_name = "Russia"

    response = requests.get(
        api_url + f"/players_teams_names/?league_name={league_name}"
    )
    assert response.status_code == 200


def test_valid_type_of_content(api_url: str):
    """
    Check if the content returned by the API is of valid type.

    Args:
        api_url (str): The URL of the API to be tested.

    Returns:
        None
    """
    league_name = "Russia"

    response = requests.get(
        api_url + f"/players_teams_names/?league_name={league_name}"
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) > 0
    assert isinstance(content[0], str)
