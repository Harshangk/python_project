from app import constant
from app.core.logging import logger
from common.schema_types import BuyStatus, clean_str, to_int
from model.buy.buy import BuyLead


def transform(
    row: dict,
    import_id,
    source: str,
    created_by: str,
) -> dict | None:
    try:
        return BuyLead(
            branch=clean_str(row.get("branch")),
            mobile=clean_str(row.get("mobile")),
            mode=clean_str(row.get("mode")),
            customer_name=clean_str(row.get("customer_name")),
            # "make": clean_str(row.get("make")),
            # "model": clean_str(row.get("model")),
            make_id=1,
            model_id=2,
            fuel_type=clean_str(row.get("fuel_type")),
            year=clean_str(row.get("year")),
            kms=to_int(row.get("kms")),
            owner=clean_str(row.get("owner")),
            client_offer=to_int(row.get("client_offer")),
            our_offer=to_int(row.get("our_offer")),
            remarks=constant.REMARKS,
            import_id=import_id,
            source=source,
            status=BuyStatus.NotAllocated.value,
            created_by=created_by,
        )
    except Exception as e:
        logger.error(f"Transform error: {str(e)}")
        logger.error(f"Transform error: {row}")
        return None
