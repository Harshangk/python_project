# app/core/logging.py
import logging
import sys

from pythonjsonlogger import jsonlogger

from common.utils import get_trace_id


class TraceIdFilter(logging.Filter):
    def filter(self, record):
        trace_id = get_trace_id()
        record.trace_id = str(trace_id) if trace_id else "-"
        return True


def setup_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(trace_id)s"
    )
    handler.setFormatter(formatter)
    handler.addFilter(TraceIdFilter())
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    return root_logger


# expose the configured logger
logger = setup_logging()
