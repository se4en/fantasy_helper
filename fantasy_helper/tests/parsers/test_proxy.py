from typing import List

import pytest
import requests

from fantasy_helper.conf.config import PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASSWORD


def test_proxy_availability():
    proxy_url = f"http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    
    try:
        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=30)
        assert response.status_code == 200
    except Exception as e:
        assert False
