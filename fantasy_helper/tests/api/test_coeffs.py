import requests
import pytest

from fantasy_helper.tests.api.fixtures import api_url
from fantasy_helper.utils.dataclasses import MatchInfo


def test_ok_response(api_url: str):
    """
    Sends a GET request to the specified API URL to retrieve the coefficients for a given league and tour.

    Args:
        api_url (str): The URL of the API to send the GET request to.

    Returns:
        None

    Raises:
        AssertionError: If the response status code is not 200.
    """
    league_name = "Russia"
    tour = "next"

    response = requests.get(api_url + f"/coeffs/?league_name={league_name}&tour={tour}")
    assert response.status_code == 200


def test_valid_type_of_content(api_url: str):
    """
    Test if the given API URL returns valid content of type list of dictionaries.

    Args:
        api_url (str): The URL of the API to be tested.

    Raises:
        AssertionError: If any of the following conditions is not met:
            - The API response status code is not 200.
            - The content returned by the API is not a list.
            - The content returned by the API is empty.
            - The first element of the content is not a dictionary.

    Returns:
        None
    """
    league_name = "Russia"
    tour = "next"

    response = requests.get(api_url + f"/coeffs/?league_name={league_name}&tour={tour}")
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) > 0
    assert isinstance(content[0], dict)
    match_info = MatchInfo(**content[0])
    assert True
