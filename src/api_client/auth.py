from src.api_client.base import BaseAPIClient
from src.api_client.models import (
    UserCreate,
    UserOut,
    TokenResponse,
    RefreshTokenRequest,
)


class AuthClient(BaseAPIClient):

    async def register(self, user: UserCreate) -> UserOut:
        response = await self._request(
            "POST",
            "/auth/register",
            json=user.model_dump()
        )
        return UserOut(**response.json())

    async def login(self, username: str, password: str) -> TokenResponse:
        response = await self._request(
            "POST",
            "/auth/login",
            data={
                "username": username,
                "password": password
            },
            headers={
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )

        data = TokenResponse(**response.json())
        self.set_access_token(data.access_token)
        return data

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        response = await self._request(
            "POST",
            "/auth/refresh_token",
            json=RefreshTokenRequest(
                refresh_token=refresh_token
            ).model_dump()
        )

        data = TokenResponse(**response.json())
        self.set_access_token(data.access_token)
        return data

    async def logout(self) -> None:
        await self._request("POST", "/auth/logout")
        self.clear_token()
