import logging
import time
from uuid import UUID, uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from common.utils import set_trace_id

logger = logging.getLogger("api.request")


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        trace_id_header = request.headers.get("X-Trace-Id")

        trace_id = UUID(trace_id_header) if trace_id_header else uuid4()

        set_trace_id(trace_id)

        start_time = time.time()

        response = await call_next(request)

        duration = round((time.time() - start_time) * 1000, 2)

        logger.info(
            "request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration,
            },
        )

        response.headers["X-Trace-Id"] = str(trace_id)

        return response
