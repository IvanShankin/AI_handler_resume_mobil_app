from src.api_client.base import BaseAPIClient
from src.api_client.exceptions import UserAlreadyRegistered, UserNotFound, APIClientError
from src.api_client.models import (
    UserCreate,
    UserOut,
    TokenResponse,
    RefreshTokenRequest,
)
from src.modile.config import get_config


class AuthClient:
    def __init__(self, api: BaseAPIClient):
        self.api = api

    async def register(self, user: UserCreate) -> UserOut:
        try:
            response = await self.api.request(
                "POST",
                "/auth/register",
                json=user.model_dump()
            )
            return UserOut(**response.json())
        except APIClientError as e:
            if e.status_code == 409:
                raise UserAlreadyRegistered()
            raise e

    async def login(self, username: str, password: str) -> TokenResponse:
        """
        :raise InvalidCredentialsException: При неверных данных
        """
        response = await self.api.request(
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
        token_storage = get_config().token_storage
        token_storage.set_access_token(data.access_token)
        token_storage.set_refresh_token(data.refresh_token)
        return data

    async def refresh_token(self, refresh_token: str) -> TokenResponse:
        try:
            response = await self.api.request(
                "POST",
                "/auth/refresh_token",
                json=RefreshTokenRequest(
                    refresh_token=refresh_token
                ).model_dump(),
                skip_refresh = True
            )
            data = TokenResponse(**response.json())

            token_storage = get_config().token_storage
            token_storage.set_access_token(data.access_token)
            token_storage.set_refresh_token(data.refresh_token)
            return data
        except APIClientError as e:
            if e.status_code == 403:
                raise UserNotFound()
            raise e

    async def logout(self) -> None:
        """Выйдет из учётной записи и сделает невалидным refresh токен"""
        await self.api.request("POST", "/auth/logout")
        token_storage = get_config().token_storage
        token_storage.clear_tokens()
