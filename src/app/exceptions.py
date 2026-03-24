class AppException(Exception):
    debug_message: str | None = None
    client_message: str

    def __new__(cls, *args, **kwargs) -> "AppException":
        if not hasattr(cls, "client_message"):
            raise AttributeError("client_message must be set")
        return super().__new__(cls, *args, **kwargs)

    def __str__(self) -> str:
        return self.debug_message or self.client_message


class Conflict(AppException):
    client_message = "Conflict."
