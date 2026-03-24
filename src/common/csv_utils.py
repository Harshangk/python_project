import csv
import io
from datetime import datetime
from typing import AsyncIterable

from fastapi.responses import StreamingResponse


def _format_value(value):
    """Fast formatter for CSV values"""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    return value


def stream_csv(rows: AsyncIterable, filename: str) -> StreamingResponse:
    """
    High-performance CSV streaming for large datasets.
    Works with async generators and millions of rows.
    """

    async def generator():
        buffer = io.StringIO()
        writer = None
        headers_written = False

        async for row in rows:

            # row may be Pydantic model or dict
            if hasattr(row, "model_dump"):
                row = row.model_dump()

            if not headers_written:
                headers = list(row.keys())
                writer = csv.writer(buffer)

                writer.writerow(headers)
                yield buffer.getvalue()
                buffer.seek(0)
                buffer.truncate(0)

                headers_written = True

            writer.writerow(_format_value(row[h]) for h in headers)

            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)

    return StreamingResponse(
        generator(),
        media_type="text/csv",
        ### if need download option
        # headers={
        #     "Content-Disposition": f'attachment; filename="{filename}"'
        # },
    )
