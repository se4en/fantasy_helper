import requests
import pytest

from fantasy_helper.tests.api.fixtures import api_url


def test_ok_response(api_url: str):
    """
    Retrieves the tour number for the given league name from the API.

    Args:
        api_url (str): The URL of the API.

    Raises:
        AssertionError: If the response status code is not 200.

    Returns:
        None
    """
    league_name = "Russia"

    response = requests.get(api_url + f"/tour_number/?league_name={league_name}")
    assert response.status_code == 200


def test_valid_type_of_content(api_url: str):
    """
    Check if the content type of the API response is valid.

    Args:
        api_url (str): The URL of the API.

    Raises:
        AssertionError: If the content type is not an integer.
    """
    league_name = "Russia"

    response = requests.get(api_url + f"/tour_number/?league_name={league_name}")
    assert isinstance(response.json(), int)
