import asyncio

from src.api_client.exceptions import Unauthorized
from src.modile.config import get_config


class TokenManager:
    def __init__(self, auth_client):
        self.auth_client = auth_client
        self._refresh_lock = asyncio.Lock()

    async def refresh_if_needed(self):
        token_storage = get_config().token_storage

        async with self._refresh_lock:
            refresh_token = token_storage.get_refresh_token()
            if not refresh_token:
                raise Unauthorized(401, {}, "No refresh token")

            data = await self.auth_client.refresh_token(refresh_token)

            token_storage.set_refresh_token(data.refresh_token)

            token_storage = get_config().token_storage
            token_storage.set_access_token(data.access_token)

            return data.access_token