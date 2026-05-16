import json

from fastapi import HTTPException, status

from app.constant import INVALID, INVALIDPAYLOAD
from app.core.logging import logger
from schema.buy.buy import EvaluationParameterRequest


async def validate_evaluation_parameters(
    evaluation_data: str,
) -> list[dict]:

    try:
        payload = json.loads(evaluation_data)

    except json.JSONDecodeError:
        logger.info("Invalid evaluation payload")
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            INVALIDPAYLOAD,
        )
    if not isinstance(payload, list):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            INVALIDPAYLOAD,
        )
    if not payload:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            INVALID,
        )

    validated_data = []
    for item in payload:
        validated = EvaluationParameterRequest(**item)
        validated_data.append(validated.model_dump())
    return validated_data
