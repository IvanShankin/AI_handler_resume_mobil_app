class APIClientError(Exception):
    def __init__(self, status_code: int = None, json: dict = None, text: str = None):
        self.status_code = status_code
        self.json = json
        self.text = text


class ServerError(APIClientError):
    def __init__(self, status_code: int, json: dict):
        self.status_code = status_code
        self.json = json


class Unauthorized(APIClientError):
    pass


class InvalidTokenException(APIClientError):
    pass


class UserNotFound(APIClientError):
    pass


class InvalidCredentialsException(APIClientError):
    pass


class UserAlreadyRegistered(APIClientError):
    pass


class InvalidCredentials(APIClientError):
    pass


class TokenExpired(APIClientError):
    pass

