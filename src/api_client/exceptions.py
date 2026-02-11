class APIClientError(Exception):
    pass


class Unauthorized(APIClientError):
    pass


class InvalidCredentials(APIClientError):
    pass


class TokenExpired(APIClientError):
    pass
