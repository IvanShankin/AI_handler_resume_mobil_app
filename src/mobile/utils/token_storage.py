import json
from pathlib import Path


class TokenStorage:
    def __init__(self, tokens_file_path: Path):
        """
        :param tokens_file_path: json файл
        """
        self._file = tokens_file_path
        self._access = None

    def _read_tokens(self) -> dict:
        if not self._file.exists():
            return {}
        try:
            return json.loads(self._file.read_text())
        except Exception:
            return {}

    def _write_tokens(self, data: dict):
        self._file.write_text(json.dumps(data))

    # ---------- Refresh token (persistent) ----------

    def set_refresh_token(self, token: str):
        data = self._read_tokens()
        data["refresh_token"] = token
        self._write_tokens(data)

    def get_refresh_token(self) -> str | None:
        data = self._read_tokens()
        return data.get("refresh_token")

    def delete_refresh_token(self):
        data = self._read_tokens()
        data.pop("refresh_token", None)
        self._write_tokens(data)

    # ---------- Access token (in memory) ----------

    def set_access_token(self, token: str):
        self._access = token

    def get_access_token(self) -> str | None:
        return self._access

    def delete_access_token(self):
        self._access = None

    # ---------- Clear ----------

    def clear_tokens(self):
        self.delete_refresh_token()
        self.delete_access_token()