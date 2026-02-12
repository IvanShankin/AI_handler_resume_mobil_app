import keyring


class TokenStorage:
    def __init__(self):
        self.SERVICE = "resume_app"
        self.access = None

    def set_refresh_token(self, token: str):
        keyring.set_password(self.SERVICE, "refresh_token", token)

    def get_refresh_token(self) -> str | None:
        return keyring.get_password(self.SERVICE, "refresh_token")

    def delete_refresh_token(self):
        keyring.delete_password(self.SERVICE, "refresh_token")


    def set_access_token(self, token: str):
        self.access = token

    def get_access_token(self) -> str | None:
        return self.access

    def delete_access_token(self):
        self.access = None

    def clear_tokens(self):
        """Очищает refresh и access токены"""
        self.delete_refresh_token()
        self.delete_access_token()
