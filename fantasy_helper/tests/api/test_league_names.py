import requests
import pytest


from fantasy_helper.tests.api.fixtures import api_url


def test_ok_response(api_url: str):
    """
    Sends a GET request to the specified API URL and checks if the response status code is 200.

    Parameters:
        api_url (str): The URL of the API.

    Returns:
        None
    """
    response = requests.get(api_url + "/leagues_names/")
    assert response.status_code == 200
