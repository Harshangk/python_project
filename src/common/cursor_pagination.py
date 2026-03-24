from typing import Optional

from fastapi import Request

from app.constant import DEFAULT_LIMIT, MAX_LIMIT


def normalize_limit(limit: Optional[int]) -> int:
    """
    Ensures limit is within allowed range.
    """
    if limit is None:
        return DEFAULT_LIMIT

    if limit <= 0:
        return DEFAULT_LIMIT

    if limit > MAX_LIMIT:
        return MAX_LIMIT

    return limit


def build_next_page_url(request: Request, cursor: int, limit: int) -> str:
    """
    Builds next page URL using cursor
    """
    params = dict(request.query_params)

    params["cursor"] = cursor
    params["limit"] = limit

    query = "&".join(f"{k}={v}" for k, v in params.items())

    return f"{request.url.path}?{query}"
