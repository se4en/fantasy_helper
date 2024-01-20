from pytest import fixture


@fixture(scope="session")
def api_url() -> str:
    """
    This fixture function returns the API URL as a string.

    :return: The API URL as a string.
    :rtype: str
    """
    yield "http://localhost:8000"
