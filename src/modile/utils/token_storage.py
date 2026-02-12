import keyring


class TokenStorage:
    SERVICE = "resume_app"

    def save_refresh(self, token: str):
        keyring.set_password(self.SERVICE, "refresh_token", token)

    def get_refresh(self) -> str | None:
        return keyring.get_password(self.SERVICE, "refresh_token")

    def delete_refresh(self):
        keyring.delete_password(self.SERVICE, "refresh_token")


_token_storage: TokenStorage = None


def init_token_storage():
    global _token_storage
    _token_storage = TokenStorage()


def get_token_storage():
    global _token_storage
    if _token_storage is None:
        raise RuntimeError("TokenStorage не инициализированно")
    return _token_storage