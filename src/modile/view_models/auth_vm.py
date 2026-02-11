from src.api_client.auth import AuthClient
from src.api_client.models import UserCreate


class AuthViewModel:
    def __init__(self, auth_client: AuthClient):
        self.auth_client = auth_client

    async def login(self, username: str, password: str):
        if not username or not password:
            return False, "Введите email и пароль"

        try:
            token = await self.auth_client.login(username, password)
            return True, token
        except Exception as e:
            return False, str(e)


class RegViewModel:
    def __init__(self, auth_client: AuthClient):
        self.auth_client = auth_client

    async def registration(self, email: str, password: str, full_name: str):
        if not email or not password or not full_name:
            return False, "Введите email, пароль и полное имя"

        try:
            user = await self.auth_client.register(UserCreate(
                username=email, password=password, full_name=full_name
            ))
            token = await self.auth_client.login(email, password)
            return True, token
        except Exception as e:
            return False, str(e)
