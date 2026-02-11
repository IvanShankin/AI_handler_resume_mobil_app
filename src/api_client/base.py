import httpx
from typing import Optional
from src.api_client.exceptions import Unauthorized, APIClientError


class BaseAPIClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self._access_token: Optional[str] = None

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            trust_env=False
        )

    def set_access_token(self, token: str):
        self._access_token = token

    def clear_token(self):
        self._access_token = None

    async def _request(self, method: str, url: str, **kwargs):
        headers = kwargs.pop("headers", {})

        if self._access_token:
            headers["Authorization"] = f"Bearer {self._access_token}"

        response = await self._client.request(
            method,
            url,
            headers=headers,
            **kwargs
        )

        if response.status_code == 401:
            raise Unauthorized("Unauthorized")

        if response.status_code >= 400:
            raise APIClientError(
                f"{response.status_code}: {response.text}"
            )

        return response

    async def close(self):
        await self._client.aclose()
