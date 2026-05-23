class AuthException(Exception): ...  # noqa


class Unauthorized(AuthException): ...  # noqa


class ForbiddenError(AuthException): ...  # noqa


class AlreadyExistsError(Exception):
    def __init__(
        self,
        lead_id: int,
        status: str,
        telecaller: str = None,
        executive: str = None,
    ):
        self.lead_id = lead_id
        self.status = status
        self.telecaller = telecaller
        self.executive = executive


class NotFound(AuthException): ...  # noqa


class CreationError(Exception): ...  # noqa


class AllocationError(Exception): ...  # noqa
