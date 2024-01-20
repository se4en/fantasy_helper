import requests
import pytest

from fantasy_helper.tests.api.fixtures import api_url
from fantasy_helper.utils.dataclasses import PlayersLeagueStats


def test_ok_response(api_url: str):
    """
    A function that sends a GET request to the specified API URL with the league name as a query parameter and
    asserts that the response status code is 200.

    Parameters:
        api_url (str): The URL of the API to send the request to.

    Returns:
        None
    """
    league_name = "Russia"

    response = requests.get(api_url + f"/lineups/?league_name={league_name}")
    assert response.status_code == 200
