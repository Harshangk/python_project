from app import constant
from app.core.logging import logger
from common.schema_types import BuyStatus, to_int


def transform(
    row: dict,
    import_id,
    source: str,
    created_by: str,
) -> dict | None:
    try:
        return {
            "branch": row.get("branch"),
            "mobile": row.get("mobile"),
            "mode": row.get("mode"),
            "customer_name": row.get("customer_name"),
            # "make": row.get("make"),
            # "model": row.get("model"),
            "make_id": 1,
            "model_id": 2,
            "fuel_type": row.get("fuel_type"),
            "year": row.get("year"),
            "kms": to_int(row.get("kms")),
            "owner": row.get("owner"),
            "client_offer": to_int(row.get("client_offer")),
            "our_offer": to_int(row.get("our_offer")),
            "remarks": constant.REMARKS,
            "import_id": import_id,
            "source": source,
            "status": BuyStatus.NotAllocated.value,
            "created_by": created_by,
        }
    except Exception as e:
        logger.error(f"Transform error: {str(e)}")
        logger.error(f"Transform error: {row}")
        return None
