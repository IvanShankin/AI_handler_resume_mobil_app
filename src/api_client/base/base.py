from typing import Optional

import httpx

from src.api_client.exceptions import Unauthorized, APIClientError
from src.modile.config import get_config


class BaseAPIClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self._access_token: Optional[str] = None
        self.token_manager = None

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            trust_env=False
        )

    def set_token_manager(self, manager):
        self.token_manager = manager

    def clear_tokens(self):
        """Очищает refresh и access токены"""
        token_storage = get_config().token_storage
        token_storage.delete_refresh_token()
        token_storage.delete_access_token()

    async def request(self, method: str, url: str, *, skip_refresh=False, **kwargs):
        headers = kwargs.pop("headers", {})

        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        response = await self._client.request(
            method,
            url,
            headers=headers,
            **kwargs
        )

        if response.status_code == 401 and not skip_refresh:
            # пробуем обновить токен
            if not self.token_manager:
                raise Unauthorized(401, response.json(), "Unauthorized")

            new_token = await self.token_manager.refresh_if_needed()
            self._access_token = new_token

            # повторяем исходный запрос
            headers["Authorization"] = f"Bearer {new_token}"

            retry_response = await self._client.request(
                method,
                url,
                headers=headers,
                **kwargs
            )

            if retry_response.status_code == 401:
                raise Unauthorized(401, retry_response.json(), "Unauthorized")

            return retry_response

        if response.status_code >= 400:
            raise APIClientError(
                status_code=response.status_code,
                json=response.json(),
                text=response.text
            )

        return response

    async def close(self):
        await self._client.aclose()
