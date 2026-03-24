import logging
from typing import Any, Callable, Coroutine, Final

from fastapi import Request, status
from fastapi.responses import JSONResponse, Response

from app.exceptions import Conflict
from auth.exceptions import ForbiddenError, NotFound, Unauthorized


async def handle_unauthorized(request: Request, exc: Unauthorized) -> JSONResponse:
    return JSONResponse(
        dict(detail="Not authenticated"),
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def handle_forbidden(request: Request, exc: ForbiddenError) -> JSONResponse:
    return JSONResponse(
        dict(detail="Access denied"),
        status_code=status.HTTP_403_FORBIDDEN,
    )


async def handle_not_found(request: Request, exc: NotFound) -> JSONResponse:
    return JSONResponse(
        dict(detail=str(exc)),
        status_code=status.HTTP_404_NOT_FOUND,
    )


async def handle_invalid_page(request: Request, exc: NotFound) -> JSONResponse:
    return JSONResponse(dict(detail=str(exc)), status_code=404)


async def handle_conflict(request: Request, exc: Conflict) -> JSONResponse:
    if exc.debug_message:
        logging.info(exc.debug_message)
    return JSONResponse(dict(detail=str(exc.client_message)), status_code=409)


EXCEPTION_HANDLERS: Final[
    dict[int | type[Exception], Callable[[Request, Any], Coroutine[Any, Any, Response]]]
] = {
    Unauthorized: handle_unauthorized,
    ForbiddenError: handle_forbidden,
    NotFound: handle_not_found,
    Conflict: handle_conflict,
}
