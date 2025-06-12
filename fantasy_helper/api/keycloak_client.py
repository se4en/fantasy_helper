import httpx
from fastapi import HTTPException

from fantasy_helper.conf.config import KEYCLOAK_BASE_URL, KEYCLOAK_SERVER_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET


class KeycloakClient:
    def __init__(self, client: httpx.AsyncClient | None = None):
        self.client = client or httpx.AsyncClient()

        self._token_url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
        self._userinfo_url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
        self._redirect_url = f"{KEYCLOAK_BASE_URL}/api/login/callback"

    async def get_tokens(self, code: str) -> dict:
        """Обмен authorization code на токены"""
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self._redirect_url,
            "client_id": KEYCLOAK_CLIENT_ID,
            "client_secret": KEYCLOAK_CLIENT_SECRET,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            response = await self.client.post(
                self._token_url, 
                data=data, 
                headers=headers
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401, detail=f"Token request failed: {response.text}"
                )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500, detail=f"Token exchange failed: {str(e)}"
            )

    async def get_user_info(self, token: str) -> dict:
        """Получить информацию о пользователе по access_token"""
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = await self.client.get(self._userinfo_url, headers=headers)
            if response.status_code != 200:
                raise HTTPException(
                    status_code=401, detail=f"Invalid access token: {response.text}"
                )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=500, detail=f"Keycloak request error: {str(e)}"
            )
