from typing import Tuple

from pydantic import ValidationError

from src.api_client.services.auth import AuthClient
from src.api_client.exceptions import UserAlreadyRegistered, UserNotFound, Unauthorized
from src.api_client.models import UserCreate, TokenResponse
from src.modile.config import get_config


class AuthViewModel:
    def __init__(self, auth_client: AuthClient):
        self.auth_client = auth_client

    async def login(self, username: str, password: str) -> Tuple[TokenResponse | None, str]:
        if not username or not password:
            return None, "Введите email и пароль"

        try:
            token = await self.auth_client.login(username, password)
            return token, "Успешная авторизация"
        except Unauthorized:
            return None, f"Неверные данные для входа"
        except Exception as e:
            return None, str(e)

    async def check_refresh_token(self) -> Tuple[TokenResponse | None, str]:
        """
        Попробует получить данные для входа с refresh токена.
        """
        token_storage = get_config().token_storage
        refresh_token = token_storage.get_refresh_token()

        if refresh_token is None:
            return None, "Нет токена"

        try:
            token = await self.auth_client.refresh_token(refresh_token)
            return token, "Успешно"
        except Unauthorized:
            token_storage.delete_refresh_token()
            return None, "Невалидный токен"
        except UserNotFound:
            token_storage.delete_refresh_token()
            return None, "Пользователь не найден"
        except Exception as e:
            return None, str(e)


class RegViewModel:
    def __init__(self, auth_client: AuthClient):
        self.auth_client = auth_client

    async def registration(self, email: str, password: str, full_name: str) -> Tuple[TokenResponse | None, str]:
        if not email or not password or not full_name:
            return None, "Введите email, пароль и полное имя"

        try:
            await self.auth_client.register(UserCreate(
                username=email, password=password, full_name=full_name
            ))
            token = await self.auth_client.login(email, password)
            return token, "Регистрация прошла успешно"
        except ValidationError:
            return None, "Введены некорректные данные. Попробуйте ещё раз"
        except UserAlreadyRegistered:
            return None, f"Пользователь с email = '{email}' уже зарегистрирован"
        except Exception as e:
            return None, str(e)
