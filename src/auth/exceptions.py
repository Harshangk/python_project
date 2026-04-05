class AuthException(Exception): ...  # noqa


class Unauthorized(AuthException): ...  # noqa


class ForbiddenError(AuthException): ...  # noqa


class NotFound(AuthException): ...  # noqa


class CreationError(Exception): ...  # noqa


class AllocationError(Exception): ...  # noqa
