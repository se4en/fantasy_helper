from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request

from fantasy_helper.api.keycloak_client import KeycloakClient


# ✅ Получаем KeycloakClient из app.state
def get_keycloak_client(request: Request) -> KeycloakClient:
    return request.app.state.keycloak_client


# ✅ Получаем токен из cookie (None, если нет)
async def get_token_from_cookie(request: Request) -> Optional[str]:
    return request.cookies.get("access_token")


# ✅ Получаем пользователя по токену
async def get_current_user(
    token: str = Depends(get_token_from_cookie),
    keycloak: KeycloakClient = Depends(get_keycloak_client),
) -> dict:
    if not token:
        # Возвращаем стандартную ошибку — редиректим позже в роутере
        raise HTTPException(status_code=401, detail="Unauthorized: No access token")
    try:
        user_info = await keycloak.get_user_info(token)

        print("user_info", user_info)

        realm_roles = user_info.get("realm_access", {}).get("roles", [])
        custom_roles = [role for role in realm_roles if role in ["basic_user", "admin_user", "premium_user"]]
        user_info["roles"] = custom_roles
        
        return user_info
    except HTTPException:
        # Токен невалиден или истек — выше можно перехватить и сделать редирект
        raise HTTPException(status_code=401, detail="Invalid token")
