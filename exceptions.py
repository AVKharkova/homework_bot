class MissingTokenError(Exception):
    """Исключение при отсутствии токенов."""
    pass


class HTTPStatusError(Exception):
    """Исключение статус-кода."""
    pass


class BadRequestError(HTTPStatusError):
    """Исключение 400 (Bad Request)."""
    pass


class NotFoundError(HTTPStatusError):
    """Исключение 404 (Not Found)."""
    pass


class ServerError(HTTPStatusError):
    """Исключение 500 (Internal Server Error)."""
    pass
